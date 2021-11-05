#!/bin/sh
starknet-compile contracts/account.cairo --output account.json --abi account_abi.json
starknet-compile contracts/briq.cairo --output briq.json --abi briq_abi.json
starknet-compile contracts/set.cairo --output set.json --abi set_abi.json
