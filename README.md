# yield-wolf-vaults

Testing and deployment scripts for YieldWolf vaults.

## Summary

This repo was prepared as a personal exercise to practice writing deployment scripts and tests for decentralised finance applications. I decided to use YieldWolf vaults and strategies as an example as I am a heavy user of that protocol and I like the code architecture they have used. I have included smart contract code of:

- the YieldWolf vault (YieldWolf.sol)
- the generic autocompound strategy (AutoCompoundStrategy.sol)
- the solidex specific autocompound strategy (ACSolidex.sol)
- uniswap and solidly pairs and routers (UniswapV2Pair.sol, BaseV1Pair.sol, UniswapV2Router.sol, BaseV1Router.sol)

Unlike many other autocompounding protocols, YieldWolf has only one vault, which a user can interact with to deploy funds to one or more strategies. The vault owns the strategies and funds can be deployed and withdrawn from a strategy by the vault. A user would typiacally interact with the deposit, earn and withdraw functions of the vault smart contract.

- The tests script includes units tests for deposit, earn and withdraw functions.
- deploy.py contains a sample deployment of YieldWolf vault and a strategy that autocompounds the wftm-tomb solidly volatile LP in the relevant Solidex farm. 


- [Yield-wolf-vaults](#yield-wolf-vaults)
  - [Summary](#summary)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Useage](#useage)
  - [Scripts](#scripts)
  - [Front end](#front-end)
  - [Testing](#testing)
  - [Linting](#linting)
- [Resources](#resources)
- [License](#license)

## Prerequisites

Please install or have installed the following:

- [nodejs and npm](https://nodejs.org/en/download/)
- [python](https://www.python.org/downloads/)

## Installation

1. [Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html), if you haven't already. Here is a simple way to install brownie.

```bash
pip install --user pipx
pipx ensurepath
# restart your terminal
pipx install eth-brownie
```

Or if you can't get `pipx` to work, via pip (it's recommended to use pipx)

```bash
pip install eth-brownie
```

2. Clone this repo

```
git clone https://github.com/0xyz-web3/yield-wolf-vaults.git
cd yield-wolf-vaults
```

1. [Install ganache-cli](https://www.npmjs.com/package/ganache-cli)

```bash
npm install -g ganache-cli
```

If you want to be able to deploy to testnets, do the following.

4. Set your environment variables

Set your `WEB3_INFURA_PROJECT_ID`, and `PRIVATE_KEY` [environment variables](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html).

You can get a `WEB3_INFURA_PROJECT_ID` by getting a free trial of [Infura](https://infura.io/). At the moment, it does need to be infura with brownie. You can find your `PRIVATE_KEY` from your ethereum wallet like [metamask](https://metamask.io/).

You'll also want an [Etherscan API Key](https://etherscan.io/apis) to verify your smart contracts.

You can add your environment variables to the `.env` file:

```bash
export WEB3_INFURA_PROJECT_ID=<PROJECT_ID>
export PRIVATE_KEY=<PRIVATE_KEY>
export ETHERSCAN_TOKEN=<YOUR_TOKEN>
```

> DO NOT SEND YOUR KEYS TO GITHUB
> If you do that, people can steal all your funds. Ideally use an account with no real money in it.

# Useage

## Scripts

```bash
brownie run scripts/deploy.py --network ftm-main-fork
```

This will deploy the YieldWolf contracts (vault and strategy which autocompounds the wftm-tomb Solidly volatile LP in the Solidex farm). You do not need to deploy these contract in order to run the tests. The tests run on the exisitng deployments of the YieldWolf vaults. If you want to run tests on your own deployment of the YieldWolf contracts you will need to first deploy the contracts and then modify the contract addresses and the pool id used in the test script. 


## Testing

```
brownie test --network ftm-main-fork
```

## Linting

```
pip install black
pip install autoflake
autoflake --in-place --remove-unused-variables -r .
black .
```
