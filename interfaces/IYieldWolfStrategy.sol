// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

interface IYieldWolfStrategy {
    function stakeToken() external view returns (address);

    function sharesTotal() external view returns (uint256);

    function earn(address _bountyHunter) external returns (uint256);

    function deposit(uint256 _depositAmount) external returns (uint256);

    function withdraw(
        uint256 _withdrawAmount,
        address _withdrawTo,
        address _bountyHunter,
        uint256 _ruleFeeAmount
    ) external returns (uint256);

    function router() external view returns (address);

    function token0() external view returns (address);

    function token1() external view returns (address);

    function totalStakeTokens() external view returns (uint256);

    function setSwapRouterEnabled(bool _enabled) external;

    function setSwapPath(
        address _token0,
        address _token1,
        address[] calldata _path
    ) external;

    function setExtraEarnTokens(address[] calldata _extraEarnTokens) external;
}