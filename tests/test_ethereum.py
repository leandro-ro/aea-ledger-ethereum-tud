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
from eth_account.messages import encode_defunct

from aea_ledger_ethereum_tud import EthereumTudWallet
from eth_account import Account

hw_keystore = "tests/data/hot_wallet_keystore/"
cw_keystore = "tests/data/cold_wallet_keystore/"


def test_overwrite():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)  # Permission to overwrite is not given ...
    try:
        wallet.perform_overwrite()  # ... and perform_overwrite() is prohibited ...
        assert False
    except Exception:  # ... therefore we expect an exception
        assert True

    wallet = EthereumTudWallet(hw_keystore, cw_keystore, True)  # Permission to overwrite is now given ...
    try:
        wallet.perform_overwrite()  # ... and perform_overwrite() is allowed ...
    except Exception:  # ... therefore we do NOT expect an exception
        assert False


def test_initialization():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    try:
        wallet.address(1)  # Should raise an exception because no public key were derived yet
        assert False
    except Exception:
        assert True


def test_derivation_one():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    wallet.public_key(1)
    addr = wallet.address(1)
    sk = wallet.private_key(1)
    acc = Account.from_key(sk)

    assert acc.address.lower() == addr.lower()  # If address matches, public  key also must match


def test_derivation_two():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    wallet.public_key(100)
    addr = wallet.address(100)
    sk = wallet.private_key(100)
    acc = Account.from_key(sk)

    assert acc.address.lower() == addr.lower()  # If address matches, public  key also must match


def test_derivation_exception_one():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    try:
        wallet.private_key(110)  # Public key must be derived first
        assert False
    except Exception:
        assert True


def test_derivation_exception_two():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    try:
        wallet.public_key(50)  # Id must be higher than all previously used ids
        assert False
    except Exception:
        assert True


def test_derivation_stress():
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    for i in range(101, 250):
        wallet.public_key(i)
        sk = wallet.private_key(i)
        addr = wallet.address(i)
        acc = Account.from_key(sk)
        assert acc.address == addr


def test_sign_message_bytes():
    """Test the signing function for byte messages."""
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    sign_bytes = wallet.sign_message(b"hello", 1)
    assert len(sign_bytes) > 0, "The len(signature) must not be 0"
    recovered_address = Account.recover_message(
        signable_message=encode_defunct(primitive=b"hello"), signature=sign_bytes
    )
    assert (
            recovered_address == wallet.address(1)
    ), "Failed to recover the correct address."


def test_sign_message_string():
    """Test the signing for string messages."""
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    sign_bytes = wallet.sign_message("hello", 100)
    assert len(sign_bytes) > 0, "The len(signature) must not be 0"
    recovered_address = Account.recover_message(
        signable_message=encode_defunct(text="hello"), signature=sign_bytes
    )
    assert (
            recovered_address == wallet.address(100)
    ), "Failed to recover the correct address."


def test_sign_transaction():
    """Test the construction, signing and submitting of a transfer transaction."""
    wallet = EthereumTudWallet(hw_keystore, cw_keystore)

    transfer_transaction = {
        # Note that the address must be in checksum format or native bytes:
        'to': '0x82fc853256B05029b3759161B32E3460Fe4eaC77',
        'value': 10000000000000000,
        'gas': 2000000,
        'gasPrice': 2500000008,
        'nonce': 1,
        'chainId': 3,  # Ropsten Testnet ID = 3
    }

    signed_transaction = wallet.sign_transaction(transfer_transaction, 150)
    assert (
            isinstance(signed_transaction, dict) and len(signed_transaction) == 5
    ), "Incorrect signed_transaction constructed."

    recovered_address = Account.recover_transaction(signed_transaction.get("raw_transaction"))
    assert (
        recovered_address == wallet.address(150)
    )
