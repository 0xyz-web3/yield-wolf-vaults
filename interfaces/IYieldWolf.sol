// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

import "../interfaces/IYieldWolfStrategy.sol";

interface IYieldWolf {
    

    function operators(address addr) external returns (bool);

    function depositFee() external view returns (uint256);

    function withdrawFee() external view returns (uint256);

    function performanceFee() external view returns (uint256);

    function performanceFeeBountyPct() external returns (uint256);

    function ruleFee() external view returns (uint256);

    function ruleFeeBountyPct() external returns (uint256);

    function feeAddress() external view returns (address);

    function stakedTokens(uint256 pid, address user) external view returns (uint256);

    function userStakedPoolLength(address _user) external view returns (uint256);

    function userStakedPoolAt(address _user, uint256 _index) external view returns (uint256);

    function deposit(uint256 _pid, uint256 _depositAmount) external;

    function depositTo(
        uint256 _pid,
        uint256 _depositAmount,
        address _to
    ) external;

    function withdraw(uint256 _pid, uint256 _withdrawAmount) external;

    // function add(IYieldWolfStrategy _strategy) public;

    // function addMany(IYieldWolfStrategy[] calldata _strategies) external;

    function emergencyWithdraw(uint256 _pid) external;

    function earn(uint256 _pid) external returns (uint256); 

    function earnMany(uint256[] calldata _pids) external;

    function userPoolRule(
        uint256 _pid,
        address _user,
        uint256 _ruleIndex
    ) external view;

    function userRuleLength(uint256 _pid, address _user) external view returns (uint256);


}