from scripts.helpful_scripts import get_account
from scripts.token_scripts import get_lp_token
from brownie import interface

def test_vault_deposit():
    account = get_account()
    get_lp_token(70, 'wftm', 'tomb', 30)

    lp_token = interface.IUniswapV2Pair('0x2A651563C9d3Af67aE0388a5c8F89b867038089e')
    lp_token_balance = lp_token.balanceOf(account)

    vault = interface.IYieldWolf('0x876F890135091381c23Be437fA1cec2251B7c117')

    lp_token.approve(vault.address, lp_token_balance, {"from": account})

    tx = vault.deposit(105, lp_token_balance, {"from": account})
    
    return tx, vault, lp_token, account


def main():
    test_vault_deposit