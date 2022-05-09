from brownie import interface, config, network, chain
from web3 import Web3

from scripts.helpful_scripts import get_account

WETH_AMOUNT = 0.01 * 10 ** 18
ROUTER_CONTRACT_ADDRESSES = {'uniswap_router': {'ftm-mainnet-fork': ['0xF491e7B69E4244ad4002BC14e878a34207E38c29'],
                                                'ftm-main-fork': ['0xF491e7B69E4244ad4002BC14e878a34207E38c29']}, 
                             'solidly_router': {'ftm-mainnet-fork': ['0xa38cd27185a464914D3046f0AB9d43356B34829D'],
                                                'ftm-main-fork': ['0xa38cd27185a464914D3046f0AB9d43356B34829D']}}

ROUTER_CONTRACT_TYPE = {'spookyswap': 'uniswap_router_v2', 
                        'solidly_router': 'base_router_v1'}

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
MAINNET_FORKS = ["mainnet-fork",
    "binance-fork",
    "matic-fork",
    "fantom-fork",
    "ftm-mainnet-fork",
    "ftm-main-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + MAINNET_FORKS

WRAPPED_NATIVE_TOKENS = {'mainnet-fork': 'weth', 
                         "ftm-main-fork": 'wftm', 
                         "ftm-mainnet-fork": 'wftm', 
                         "matic-fork": "wmatic",
                         "basc-main-fork": 'wbnb',
                         "avax-main-fork": 'wavax'}

def get_weth(amount=WETH_AMOUNT, account=get_account()):
    """Mints WETH by depositing ETH."""
    weth = interface.IWETH(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": amount})
    tx.wait(1)
    return tx


def approve_token(amount, spender, token_address, account=get_account()):
    """Approves the token for the spender to spend."""
    token = interface.IERC20(token_address)
    tx = token.approve(spender, amount, {"from": account})
    tx.wait(1)
    return tx

def get_token_contract(token_name):
    if network.show_active() in MAINNET_FORKS:
        if token_name in WRAPPED_NATIVE_TOKENS[network.show_active()]:
            return interface.IWETH(config["networks"][network.show_active()][token_name])
        else:
            return interface.IERC20(config["networks"][network.show_active()][token_name])
        
def get_wrapped_ftm(ftm_to_be_wrapped):
    """Mints WFTM by depositing FTM."""
    account = get_account()
    wftm = interface.IWETH(config["networks"][network.show_active()]["wftm"])
    tx = wftm.deposit({"from": account, "value": ftm_to_be_wrapped})
    tx.wait(1)
    return tx, wftm

def swap_token_for_token(token0_name, token1_name, token0_amount, router_type):
    account = get_account()
    token0_address = config["networks"][network.show_active()][token0_name]
    token1_address = config["networks"][network.show_active()][token1_name]
    
    if token0_name == 'wftm':
        token0_contract = interface.IWETH(token0_address)
    else:
        token0_contract = interface.IERC20(token0_address)
        
    if router_type == 'uniswap':
        # get spookyswap router contract
        router_contract = interface.IUniswapV2Router02(config["networks"][network.show_active()]["spookyswap_router"])
        # get expected token1 amounts out for amount of token0
        amount_out = router_contract.getAmountsOut(token0_amount, [token0_address, token1_address])[1]
        # specify route to be taken for token exchange
        routes = [token0_address, token1_address]
        # approve token0 to be spent by router contract
        tx = token0_contract.approve(router_contract, token0_amount, {"from": account})
        tx.wait(1)
        # swap token0 to token1
        tx = router_contract.swapExactTokensForTokens(token0_amount, amount_out, routes, account, chain.time() + 10, {"from": account})
        tx.wait(1)
    elif router_type == 'solidly':
        # get spookyswap router contract
        router_contract = interface.IBaseV1Router01(config["networks"][network.show_active()]["solidly_router"])
        # get expected token1 amounts out for amount of token0. amount_out is a tuple (float token0_in, float token1_out, bool stable_route)
        amounts_out = router_contract.getAmountOut(token0_amount, token0_address, token1_address)
        # specify route to be taken for token exchange. Soldily router also requires a boolean value indicating whether 
        # the stable pool for the token pair should be used. 
        routes = [token0_address, token1_address, amounts_out[1]]
        # approve token0 to be spent by router contract
        tx = token0_contract.approve(router_contract, token0_amount, {"from": account})
        tx.wait(1)
        # swap token0 to token1
        tx = router_contract.swapExactTokensForTokensSimple(token0_amount, amounts_out[0], token0_address, token1_address, amounts_out[1], account, chain.time() + 10, {"from": account})
        tx.wait(1)
    return tx, router_contract

def add_liquidity(router, token0_name, token0_amount, token1_name, route_is_stable):
    account = get_account()
    token0_contract = get_token_contract(token0_name)
    token1_contract = get_token_contract(token1_name)
    if router.address in ROUTER_CONTRACT_ADDRESSES['uniswap_router'][network.show_active()]:
        amount_out = router.getAmountsOut(token0_amount, [token0_contract.address, token1_contract.address])[1]
        token0_contract.approve(router, token0_amount, {"from": account})
        token1_contract.approve(router, amount_out, {"from": account})
        slippage_allowed = 1 # %
        tx = router.addLiquidity(token0_contract.address, 
                            token1_contract.address, 
                            token0_amount, 
                            amount_out, 
                            token0_amount*(1-slippage_allowed/100), 
                            amount_out*(1-slippage_allowed/100), 
                            account,
                            chain.time() + 10,
                            {"from": account})
        print('Liquidity added to uniswap router')
        
    elif router.address in ROUTER_CONTRACT_ADDRESSES['solidly_router'][network.show_active()]:
        amounts_out = router.getAmountOut(token0_amount, token0_contract.address, token1_contract.address)
        token0_contract.approve(router, token0_amount, {"from": account})
        token1_contract.approve(router, amounts_out[0], {"from": account})
        slippage_allowed = 1 # %
        tx = router.addLiquidity(
            token0_contract.address, 
            token1_contract.address,
            route_is_stable,
            token0_amount, 
            amounts_out[0], 
            token0_amount*(1-slippage_allowed/100), 
            amounts_out[0]*(1-slippage_allowed/100), 
            account,
            chain.time() + 10,
            {"from": account})
        print('Liquidity added to solidly router')
        pass
    else:
        print('Invalid router')
    
    return tx

def get_lp_token(ftm_to_be_wrapped, token0_name, token1_name, router_type, route_is_stable):
    # get accounts
    account = get_account()
    # get wftm from ftm
    tx1, wftm = get_wrapped_ftm(ftm_to_be_wrapped)
    print(wftm.balanceOf(account))
    # get token0 from wftm or ftm
    if token0_name != 'wftm':
        tx2, router = swap_token_for_token('wftm', token0_name, ftm_to_be_wrapped/2, router_type)
        token0_contract = interface.IERC20(config["networks"][network.show_active()][token0_name])
        print(token0_contract.balanceOf(account))
    # get token1 from wftm or ftm
    if token1_name != 'wftm':
        tx3, router = swap_token_for_token('wftm', token1_name, ftm_to_be_wrapped/2, router_type)
        token1_contract = interface.IERC20(config["networks"][network.show_active()][token1_name])
        print(token1_contract.balanceOf(account))
    # get token0 balance
    if token0_name != 'wftm':
         token0_contract = interface.IERC20(config["networks"][network.show_active()][token0_name])
         token0_balance = token0_contract.balanceOf(account)
    else:
        token0_balance = ftm_to_be_wrapped/2
    # add liquidity to token0/token1 spookyswap/solidly pool
    tx4 = add_liquidity(router, token0_name, token0_balance, token1_name, route_is_stable)
    if token0_name == 'wftm':
        token0_contract = wftm
        
    print(router, token0_name, token0_contract, token0_balance, token1_name, token1_contract)
    return router