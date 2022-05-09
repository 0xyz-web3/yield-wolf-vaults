from brownie import (
    network,
    accounts,
    config,
    Contract,
    web3,
    UniswapV2Router02,
    BaseV1Router01,
    WrappedFtm
)
import time

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
MAINNET_FORKS = ["mainnet-fork",
    "binance-fork",
    "matic-fork",
    "fantom-fork",
    "ftm-mainnet-fork",
    "ftm-main-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + MAINNET_FORKS

# Etherscan usually takes a few blocks to register the contract has been deployed
BLOCK_CONFIRMATIONS_FOR_VERIFICATION = 6

DECIMALS = 18
INITIAL_PRICE_FEED_VALUE = web3.toWei(2000, "ether")
BASE_FEE = 100000000000000000  # The premium
GAS_PRICE_LINK = 1e9  # Some value calculated depending on the Layer 1 cost and Link


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])