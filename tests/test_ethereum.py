# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""This module contains the tests of the ethereum module."""

import pytest
from aea_ledger_ethereum_tud import (
    EthereumTudWallet
)

from tests.conftest import DEFAULT_GANACHE_CHAIN_ID


def test_creation(ethereum_private_key_file):
    """Test the creation of the crypto_objects."""
    assert EthereumCrypto(), "Managed to initialise the eth_account"
    assert EthereumCrypto(
        ethereum_private_key_file
    ), "Managed to load the eth private key"


def test_initialization():
    """Test the initialisation of the variables."""
    account = EthereumCrypto()
    assert account.entity is not None, "The property must return the account."
    assert (
        account.address is not None and type(account.address) == str
    ), "After creation the display address must not be None"
    assert (
        account.public_key is not None and type(account.public_key) == str
    ), "After creation the public key must no be None"
    assert account.entity is not None, "After creation the entity must no be None"


def test_sign_message(ethereum_private_key_file):
    """Test the signing and the recovery function for the eth_crypto."""
    account = EthereumCrypto(ethereum_private_key_file)
    sign_bytes = account.sign_message(message=b"hello")
    assert len(sign_bytes) > 0, "The len(signature) must not be 0"
    recovered_addresses = EthereumApi.recover_message(
        message=b"hello", signature=sign_bytes
    )
    assert len(recovered_addresses) == 1, "Wrong number of addresses recovered."
    assert (
        recovered_addresses[0] == account.address
    ), "Failed to recover the correct address."


def test_sign_message_public_key(ethereum_private_key_file):
    """Test the signing and the recovery function for the eth_crypto."""
    account = EthereumCrypto(ethereum_private_key_file)
    sign_bytes = account.sign_message(message=b"hello")
    assert len(sign_bytes) > 0, "The len(signature) must not be 0"
    recovered_public_keys = EthereumApi.recover_public_keys_from_message(
        message=b"hello", signature=sign_bytes
    )
    assert len(recovered_public_keys) == 1, "Wrong number of public keys recovered."
    assert (
        EthereumApi.get_address_from_public_key(recovered_public_keys[0])
        == account.address
    ), "Failed to recover the correct address."


def test_sign_transaction(
    ethereum_testnet_config, ganache, ethereum_private_key_file
):
    """Test the construction, signing and submitting of a transfer transaction."""
    account = EthereumCrypto(private_key_path=ethereum_private_key_file)
    ec2 = EthereumCrypto()
    ethereum_api = EthereumApi(**ethereum_testnet_config)

    amount = 40000
    tx_nonce = ethereum_api.generate_tx_nonce(ec2.address, account.address)
    transfer_transaction = ethereum_api.get_transfer_transaction(
        sender_address=account.address,
        destination_address=ec2.address,
        amount=amount,
        tx_fee=30000,
        tx_nonce=tx_nonce,
        chain_id=DEFAULT_GANACHE_CHAIN_ID,
    )
    assert (
        isinstance(transfer_transaction, dict) and len(transfer_transaction) == 7
    ), "Incorrect transfer_transaction constructed."

    signed_transaction = account.sign_transaction(transfer_transaction)
    assert (
        isinstance(signed_transaction, dict) and len(signed_transaction) == 5
    ), "Incorrect signed_transaction constructed."


