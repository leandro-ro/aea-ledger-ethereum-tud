# Author: Leandro Rometsch, 2021
# Email: leandro@rometsch.org
# TU Darmstadt, Chair of Applied Cryptography

"""Ethereum module wrapping the public and private key cryptography and ledger api."""
from .tudwallet import wallet as tud
from typing import Dict, Union, cast

from eth_account.datastructures import HexBytes, SignedTransaction
from eth_utils import keccak

from aea.common import JSONLike


class SignedTransactionTranslator:
    """Translator for SignedTransaction."""

    @staticmethod
    def to_dict(signed_transaction: SignedTransaction) -> Dict[str, Union[str, int]]:
        """Write SignedTransaction to dict."""
        signed_transaction_dict = {
            "raw_transaction": signed_transaction.rawTransaction.hex(),
            "hash": signed_transaction.hash.hex(),
            "r": signed_transaction.r,
            "s": signed_transaction.s,
            "v": signed_transaction.v,
        }
        return signed_transaction_dict

    @staticmethod
    def from_dict(signed_transaction_dict: JSONLike) -> SignedTransaction:
        """Get SignedTransaction from dict."""
        if (
                not isinstance(signed_transaction_dict, dict)
                and len(signed_transaction_dict) == 5
        ):
            raise ValueError(  # pragma: nocover
                f"Invalid for conversion. Found object: {signed_transaction_dict}."
            )
        signed_transaction = SignedTransaction(
            rawTransaction=HexBytes(signed_transaction_dict["raw_transaction"]),
            hash=HexBytes(signed_transaction_dict["hash"]),
            r=signed_transaction_dict["r"],
            s=signed_transaction_dict["s"],
            v=signed_transaction_dict["v"],
        )
        return signed_transaction


class EthereumTudWallet:
    """Class wrapping the Account Generation for the ethereum tudwallet."""

    def __init__(self, hot_wallet_path: str, cold_wallet_path: str, enable_overwrite=False) -> None:
        """
        Instantiate an ethereum tudwallet object.

        :param hot_wallet_path: specifies the storage location of the hot wallet
        :param cold_wallet_path: specifies the storage location of the cold wallet
        :param enable_overwrite: enables perform_overwrite() of this object
        """
        self.__wallet = tud.Wallet(hot_wallet_path, cold_wallet_path)
        self.__overwrite_protection = True

        key_pair_existing = False
        try:
            self.__wallet.generate_master_key(overwrite=False)  # Raises an exception if there is already a key pair
        except Exception:
            key_pair_existing = True

        if enable_overwrite:
            if not key_pair_existing:
                raise Exception("No key pair existing, therefore no reason for the intention to overwrite")
            self.__overwrite_protection = False

    def _reset_overwrite_protection(self):
        """
        Re-engages the overwrite protection to prevent accidental loss of keys

        """
        self.__overwrite_protection = True

    def perform_overwrite(self):
        """
        Overwrites existing keys iff overwrite protection is deactivated (set to False). Use with caution!

        """
        if not self.__overwrite_protection:
            self._reset_overwrite_protection()
            self.__wallet.generate_master_key(overwrite=True)
        else:
            raise Exception("Overwrite protection active. "
                            "Create new EthereumTudWallet object with enable_overwrite = True")

    def private_key(self, derivation_id: int) -> str:
        """
        Return an earlier derived private key by its derivation id.

        :param derivation_id: specify which private key to get
        :return: a private key string
        """
        self._reset_overwrite_protection()

        session_secret_key = self.__wallet.secret_key_derive(derivation_id)
        return session_secret_key.key

    def public_key(self, derivation_id: int) -> str:
        """
        Return an earlier derived public key by its derivation id.

        :param derivation_id: specify which public key to get
        :return: a public key string in hex format
        """
        self._reset_overwrite_protection()

        session_public_key = self.__wallet.public_key_derive(derivation_id)
        x = session_public_key.x[2:]
        y = session_public_key.y[2:]

        if not len(x) % 2 == 0:
            x = "0" + x
        if not len(y) % 2 == 0:
            y = "0" + y

        pk = keccak(hexstr=x + y)
        return "0x" + pk.hex()

    def address(self, derivation_id: int) -> str:
        """
        Return the address for the a specific key pair.

        :param derivation_id: specify which address to get
        :return: a display_address str
        """
        self._reset_overwrite_protection()

        if derivation_id not in self.__wallet.get_all_ids():
            raise Exception("Derive public key with derivation_id = " + str(derivation_id) + " first!")

        session_public_key = self.__wallet.public_key_derive(derivation_id)
        return session_public_key.address

    def sign_message(self, message, derivation_id: int) -> str:
        """
        Sign a message in bytes string or string form.

        :param message: the message to be signed, e.g. b"hello" or "hello"
        :param derivation_id: specify which account to use for signing
        :return: signature of the message in string form
        """
        self._reset_overwrite_protection()

        signed_message = self.__wallet.sign_message(message, derivation_id)
        sig = str(signed_message.signature.hex())
        return sig

    def sign_transaction(self, transaction: JSONLike, derivation_id: int) -> JSONLike:
        """
        Sign a transaction in bytes string form.

        :param transaction: the transaction to be signed
        :param derivation_id: specify which account to use for signing
        :return: signed transaction
        """
        self._reset_overwrite_protection()

        signed_transaction = self.__wallet.sign_transaction(transaction, derivation_id)

        signed_transaction_dict = SignedTransactionTranslator.to_dict(
            signed_transaction
        )
        return cast(JSONLike, signed_transaction_dict)

    def derivation_ids(self) -> list:
        """
        Returns all ids of already derived public keys.

        :return: all ids used to derive public keys earlier
        """
        self._reset_overwrite_protection()

        return self.__wallet.get_all_ids()
