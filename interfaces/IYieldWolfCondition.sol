// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

interface IYieldWolfCondition {
    function isCondition() external view returns (bool);

    function check(
        address strategy,
        address user,
        uint256 pid,
        uint256[] memory intInputs,
        address[] memory addrInputs
    ) external view returns (bool);
}