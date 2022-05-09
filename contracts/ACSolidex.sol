// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';

import './AutoCompoundStrategy.sol';

interface IFarm {
    function deposit(address _pool, uint256 _amount) external;

    function withdraw(address _pool, uint256 _amount) external;

    function tokenForPool(address _pool) external view returns (address);

    function getReward(address[] calldata pools) external;
}

interface SolidlyRouter {
    function swapExactTokensForTokensSimple(
        uint256 amountIn,
        uint256 amountOutMin,
        address tokenFrom,
        address tokenTo,
        bool stable,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function addLiquidity(
        address tokenA,
        address tokenB,
        bool stable,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    )
        external
        returns (
            uint256 amountA,
            uint256 amountB,
            uint256 liquidity
        );
}

/**
 * @title AutoCompound Solidex
 * @notice strategy for auto-compounding on pools using solidex contracts
 * @author YieldWolf
 */
contract ACSolidex is AutoCompoundStrategy {
    using SafeERC20 for IERC20;

    IERC20 public solid = IERC20(0x888EF71766ca594DED1F0FA3AE64eD2941740A20);
    bool public stable = false;

    function _farmDeposit(uint256 amount) internal override {
        IERC20(stakeToken).safeIncreaseAllowance(masterChef, amount);
        IFarm(masterChef).deposit(address(stakeToken), amount);
    }

    function _farmWithdraw(uint256 amount) internal override {
        IFarm(masterChef).withdraw(address(stakeToken), amount);
    }

    function _farmEmergencyWithdraw() internal override {
        IFarm(masterChef).withdraw(address(stakeToken), _totalStaked());
    }

    function _totalStaked() internal view override returns (uint256 amount) {
        address pool = IFarm(masterChef).tokenForPool(address(stakeToken));
        if (pool != address(0)) {
            amount = IERC20(pool).balanceOf(address(this));
        }
    }

    function _farmHarvest() internal override {
        address[] memory pools = new address[](1);
        pools[0] = address(stakeToken);
        IFarm(masterChef).getReward(pools);
    }

    function earn(address _bountyHunter) external override onlyOwner returns (uint256 bountyReward) {
        if (paused()) {
            return 0;
        }

        // harvest earn tokens
        uint256 wnativeAmountBefore = IERC20(WNATIVE).balanceOf(address(this));
        _farmHarvest();

        uint256 earnBalance = earnToken.balanceOf(address(this));
        uint256 solidBalance = solid.balanceOf(address(this));
        if (earnBalance > 0) {
            earnToNative(earnToken, earnBalance);
        }
        if (solidBalance > 0) {
            earnToNative(solid, solidBalance);
        }

        uint256 harvestAmount = IERC20(WNATIVE).balanceOf(address(this)) - wnativeAmountBefore;

        if (harvestAmount > 0) {
            bountyReward = _distributeFees(harvestAmount, _bountyHunter);
        }
        uint256 wnativeAmount = IERC20(WNATIVE).balanceOf(address(this));

        // if no token0, then stake token is a single token: Swap earn token for stake token
        if (address(token0) == address(0)) {
            if (address(stakeToken) != WNATIVE) {
                _safeSwap(wnativeAmount, swapPath[WNATIVE][address(stakeToken)], address(this), false);
            }
            _farm();
            return bountyReward;
        }

        // stake token is a LP token: Swap earn token for token0 and token1 and add liquidity
        if (WNATIVE != address(token0)) {
            _safeSwap(wnativeAmount / 2, swapPath[WNATIVE][address(token0)], address(this), false);
        }
        if (WNATIVE != address(token1)) {
            _safeSwap(wnativeAmount / 2, swapPath[WNATIVE][address(token1)], address(this), false);
        }
        uint256 token0Amt = token0.balanceOf(address(this));
        uint256 token1Amt = token1.balanceOf(address(this));
        if (token0Amt > 0 && token1Amt > 0) {
            token0.safeIncreaseAllowance(address(liquidityRouter), token0Amt);
            token1.safeIncreaseAllowance(address(liquidityRouter), token1Amt);
            SolidlyRouter(address(liquidityRouter)).addLiquidity(
                address(token0),
                address(token1),
                stable,
                token0Amt,
                token1Amt,
                0,
                0,
                address(this),
                block.timestamp
            );
        }

        _farm();
        return bountyReward;
    }

    function _distributeFees(uint256 _amount, address _bountyHunter) internal override returns (uint256) {
        uint256 bountyReward = 0;
        uint256 bountyRewardPct = _bountyHunter == address(0) ? 0 : yieldWolf.performanceFeeBountyPct();
        uint256 performanceFee = (_amount * yieldWolf.performanceFee()) / 10000;
        bountyReward = (performanceFee * bountyRewardPct) / 10000;
        uint256 platformPerformanceFee = performanceFee - bountyReward;
        if (platformPerformanceFee > 0) {
            IERC20(WNATIVE).safeTransfer(yieldWolf.feeAddress(), platformPerformanceFee);
        }
        if (bountyReward > 0) {
            IERC20(WNATIVE).safeTransfer(_bountyHunter, bountyReward);
        }
        return bountyReward;
    }

    function earnToNative(IERC20 _token, uint256 _amount) internal {
        _token.safeIncreaseAllowance(address(liquidityRouter), _amount);
        SolidlyRouter(address(liquidityRouter)).swapExactTokensForTokensSimple(
            _amount,
            0,
            address(_token),
            WNATIVE,
            false,
            address(this),
            block.timestamp
        );
    }

    function tokenToEarn(address _token) public override nonReentrant whenNotPaused {
        address pool = IFarm(masterChef).tokenForPool(address(stakeToken));
        require(_token != pool && _token != WNATIVE && _token != address(solid), 'tokenToEarn: NOT_ALLOWED');
        uint256 amount = IERC20(_token).balanceOf(address(this));
        if (amount > 0 && _token != address(earnToken) && _token != address(stakeToken)) {
            address[] memory path = swapPath[_token][address(earnToken)];
            if (path.length == 0) {
                path = new address[](2);
                path[0] = WNATIVE;
                path[1] = address(earnToken);
            }
            if (
                path[0] != address(earnToken) &&
                path[0] != address(stakeToken) &&
                path[0] != address(WNATIVE) &&
                path[0] != address(solid) &&
                path[0] != pool
            ) {
                _safeSwap(amount, path, address(this), true);
            }
            emit TokenToEarn(_token);
        }
    }
}