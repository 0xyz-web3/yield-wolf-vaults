from scripts.helpful_scripts import get_account
from brownie import ACSolidex, YieldWolf, interface
from web3 import Web3
from scripts.token_scripts import get_lp_token, get_wrapped_ftm

AMOUNT_OF_FTM_TO_EXCHANGE = 20 * 10 ** 18
FTM_TO_BE_WRAPPED = 10 * 10 ** 18

TOKEN0_NAME = 'wftm'
TOKEN1_NAME = 'tomb'
LIQUIDITY_PAIR_NAME = 'wftm_tomb_spookyswap_pair'
ROUTER_CONTRACT_ADDRESSES = {'uniswap_router': {'ftm-mainnet-fork': ['0xF491e7B69E4244ad4002BC14e878a34207E38c29']}, 
                             'solidly_router': {'ftm-mainnet-fork': ['0xa38cd27185a464914D3046f0AB9d43356B34829D']}}
def deploy_vault():
    account = get_account()
    fee_address = account
    vault = YieldWolf.deploy(fee_address, {"from": account})
    return vault
    

def deploy_strategy():
    account = get_account()
    strategy = ACSolidex.deploy({"from": account})
    
    strategy_contract = ACSolidex[-1]
    vault = YieldWolf[-1]
    
    POOL_ID = 0
    IS_LP = True
    YIELD_WOLF_CONTRACT = vault.address
    EARN_TOKEN = "0xd31fcd1f7ba190dbc75354046f6024a9b86014d7"
    STAKE_TOKEN = "0x60a861cd30778678e3d613db96139440bd333143"
    MASTERCHEF = "0x26e1a0d851cf28e697870e1b7f053b605c8b060f"
    SWAP_ROUTER = "0xf491e7b69e4244ad4002bc14e878a34207e38c29"
    LIQUIDITY_ROUTER = "0xa38cd27185a464914d3046f0ab9d43356b34829d"
    WNATIVE = "0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83"
    ADDRESSES = [YIELD_WOLF_CONTRACT, STAKE_TOKEN, EARN_TOKEN, MASTERCHEF, SWAP_ROUTER, LIQUIDITY_ROUTER, WNATIVE]
    
    EARN_TO_TOKEN0_PATH = ["0x6c021Ae822BEa943b2E66552bDe1D2696a53fbB7"]
    EARN_TO_TOKEN1_PATH = ["0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83"]
    TOKEN0_TO_EARN_PATH = ["0x6c021Ae822BEa943b2E66552bDe1D2696a53fbB7"]
    TOKEN1_TO_EARN_PATH = ["0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83"]
    
    print(f"Strategy initialized: {strategy_contract.initialized()}")
    strategy_contract.initialize(POOL_ID, IS_LP, ADDRESSES, EARN_TO_TOKEN0_PATH, EARN_TO_TOKEN1_PATH, TOKEN0_TO_EARN_PATH, TOKEN1_TO_EARN_PATH)
    print(f"Strategy initialized: {strategy_contract.initialized()}")
    
    return strategy

def add_strategy_to_vault(vault, strategy):
    account = get_account()
    vault.add(strategy, {"from": account})
    print("Strategy added to vault.")

def get_wrapped_ftm_deploy(FTM_TO_BE_WRAPPED):
    tx, wrapped_ftm_contract = get_wrapped_ftm(FTM_TO_BE_WRAPPED)
    return tx, wrapped_ftm_contract
    
def deposit_stake_token_in_vault(vault, strategy, ftm_to_be_wrapped, token0_name, token1_name, router_type, route_is_stable):
    account = get_account()
    router = get_lp_token(ftm_to_be_wrapped, token0_name, token1_name, router_type, route_is_stable)
    lp_token = interface.IBaseV1Pair(strategy.stakeToken())
    lp_token_balance = lp_token.balanceOf(account)
    print(f'lp token balance: {lp_token_balance}')
    tx =lp_token.approve(vault, lp_token_balance, {"from": account})
    tx.wait(1) 
    vault.deposit(0, lp_token_balance, {"from": account})
    print("deposited in vault")
    
    return tx


def main():
    vault = deploy_vault()
    strategy = deploy_strategy()
    add_strategy_to_vault(vault, strategy)
    deposit_stake_token_in_vault(vault, strategy, 50*10**18, TOKEN0_NAME, TOKEN1_NAME, 'solidly', False)
    
