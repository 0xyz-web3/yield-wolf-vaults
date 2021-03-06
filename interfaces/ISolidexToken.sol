// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';

interface ISolidexToken is IERC20 {
    function mint(address _to, uint256 _value) external returns (bool);
}