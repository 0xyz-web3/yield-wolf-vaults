// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

import "../interfaces/erc20.sol";
import "../library/Math.sol";

interface IBaseV1Router01 {

    // fetches and sorts the reserves for a pair
    function getReserves(address tokenA, address tokenB, bool stable) external  view returns (uint reserveA, uint reserveB);

    // performs chained getAmountOut calculations on any number of pairs
    function getAmountOut(uint amountIn, address tokenIn, address tokenOut) external view returns (uint amount, bool stable); 

    // performs chained getAmountOut calculations on any number of pairs
    function getAmountsOut(uint amountIn, address[] memory routes) external  view returns (uint[] memory amounts);

    function quoteAddLiquidity(address tokenA, address tokenB, bool stable, uint amountADesired, uint amountBDesired) external view returns (uint amountA, uint amountB, uint liquidity);

    function quoteRemoveLiquidity(address tokenA, address tokenB, bool stable, uint liquidity) external view returns (uint amountA, uint amountB);

    function addLiquidity(address tokenA, address tokenB, bool stable, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline) external returns (uint amountA, uint amountB, uint liquidity);

    function addLiquidityFTM(address token, bool stable, uint amountTokenDesired, uint amountTokenMin, uint amountFTMMin, address to, uint deadline) external payable returns (uint amountToken, uint amountFTM, uint liquidity);

    function removeLiquidity(address tokenA, address tokenB, bool stable, uint liquidity, uint amountAMin, uint amountBMin, address to, uint deadline) external  returns (uint amountA, uint amountB);

    function removeLiquidityFTM(address token, bool stable, uint liquidity, uint amountTokenMin, uint amountFTMMin, address to, uint deadline) external  returns (uint amountToken, uint amountFTM);

    function removeLiquidityWithPermit(address tokenA,  address tokenB,  bool stable, uint liquidity, uint amountAMin, uint amountBMin, address to, uint deadline, bool approveMax, uint8 v, bytes32 r, bytes32 s) external returns (uint amountA, uint amountB);

    function removeLiquidityFTMWithPermit(address token, bool stable, uint liquidity, uint amountTokenMin, uint amountFTMMin, address to, uint deadline, bool approveMax, uint8 v, bytes32 r, bytes32 s) external returns (uint amountToken, uint amountFTM);

    function swapExactTokensForTokensSimple(uint amountIn, uint amountOutMin, address tokenFrom, address tokenTo, bool stable, address to, uint deadline) external returns (uint[] memory amounts);

    function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata routes, address to, uint deadline) external returns (uint[] memory amounts);

    function swapExactFTMForTokens(uint amountOutMin, address[] calldata routes, address to, uint deadline) external payable returns (uint[] memory amounts);











}