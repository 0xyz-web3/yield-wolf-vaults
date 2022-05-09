from scripts.helpful_scripts import get_account
from scripts.token_scripts import get_lp_token
from brownie import interface, chain
import pytest
from web3 import Web3

YIELDWOLF_VAULT = '0x876F890135091381c23Be437fA1cec2251B7c117'
WFTM_TOMB_SPOOKYSWAP_LP_TOKEN_ADDRESS = '0x2A651563C9d3Af67aE0388a5c8F89b867038089e'
WFTM_TOMB_SOLIDLY_VOLATILE_LP_TOKEN_ADDRESS = '0x60a861Cd30778678E3d613db96139440Bd333143'
WFTM_TOMB_SPOOKYSWAP_VAULT_ID = 105
WFTM_TOMB_SOLIDLY_VOLATILE_VAULT_ID = 421
FTM_TO_CONVERT_TO_WFTM = 10 * 10 ** 18
TOKEN0_NAME = 'wftm'
TOKEN1_NAME = 'tomb'
ROUTER_TYPE_UNISWAP = 'uniswap'
ROUTER_TYPE_SOLIDLY = 'solidly'
STABLE_POOL = False


@pytest.fixture(params=['uniswap', 'solidly'])
def prepare_tests(request):
    account = get_account()
    get_lp_token(FTM_TO_CONVERT_TO_WFTM, TOKEN0_NAME, TOKEN1_NAME, request.param, STABLE_POOL)
    if request.param == 'uniswap':
        lp_token = interface.IUniswapV2Pair(WFTM_TOMB_SPOOKYSWAP_LP_TOKEN_ADDRESS)
    elif request.param == 'solidly':
        lp_token = interface.IBaseV1Pair(WFTM_TOMB_SOLIDLY_VOLATILE_LP_TOKEN_ADDRESS)
    else:
        print("Urecognized router")
    
    vault = interface.IYieldWolf(YIELDWOLF_VAULT)
    
    return account, lp_token, vault, request.param

    
def test_vault_deposit(prepare_tests):

    (account, lp_token, vault, router_type) = prepare_tests
    lp_token_balance = lp_token.balanceOf(account)
    tx = lp_token.approve(vault.address, lp_token_balance, {"from": account})
    print("lp token approved")
    tx.wait(1) 
       
    if router_type == 'uniswap':
        vault_id = WFTM_TOMB_SPOOKYSWAP_VAULT_ID
        
    elif router_type == 'solidly':
        vault_id = WFTM_TOMB_SOLIDLY_VOLATILE_VAULT_ID

    tx1 = vault.deposit(vault_id, lp_token_balance, {"from": account})
    print("deposited in vault")
    staked_tokens = round(Web3.fromWei(vault.stakedTokens(vault_id, account), "ether"), 2)
    expected_staked_tokens = round(Web3.fromWei(lp_token_balance, "ether"), 2)
    print("asserting")
    assert staked_tokens == expected_staked_tokens

def test_vault_earn(prepare_tests):
    (account, lp_token, vault, router_type) = prepare_tests

    lp_token_balance = lp_token.balanceOf(account)
    lp_token.approve(vault.address, lp_token_balance, {"from": account})
    
    if router_type == 'uniswap':
        vault_id = WFTM_TOMB_SPOOKYSWAP_VAULT_ID
        
    elif router_type == 'solidly':
        vault_id = WFTM_TOMB_SOLIDLY_VOLATILE_VAULT_ID
        
    tx1 = vault.deposit(vault_id, lp_token_balance, {"from": account})
    print("deposited in vault")
    vault_balance_before = vault.stakedTokens(vault_id, account)
    chain.mine(100)
    tx2 = vault.earn(vault_id, {"from": account})
    vault_balance_after = vault.stakedTokens(vault_id, account)
    
    assert vault_balance_after > vault_balance_before
    
    
def test_vault_withdraw(prepare_tests):
    (account, lp_token, vault, router_type) = prepare_tests

    lp_token_balance = lp_token.balanceOf(account)
    lp_token.approve(vault.address, lp_token_balance, {"from": account})
    
    if router_type == 'uniswap':
        vault_id = WFTM_TOMB_SPOOKYSWAP_VAULT_ID
        
    elif router_type == 'solidly':
        vault_id = WFTM_TOMB_SOLIDLY_VOLATILE_VAULT_ID

    tx = vault.deposit(vault_id, lp_token_balance, {"from": account})
    vault_balance = vault.stakedTokens(vault_id, account)
    vault.withdraw(vault_id, vault_balance, {"from": account})
    
    assert round(Web3.fromWei(vault.stakedTokens(vault_id, account), "ether"), 2) == 0
    assert round(Web3.fromWei(lp_token.balanceOf(account), "ether"), 2) == round(Web3.fromWei(vault_balance, "ether"), 2)


