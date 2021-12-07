# aea-ledger-ethereum-tud
This project wraps a custom ethereum wallet to make it compatible with the [AEA framework plug-in architecture](https://docs.fetch.ai/aea/ledger-integration/#ledger-plug-in-architecture). The wallet utilizes cryptographic operations based on ["A Formal Treatment of Deterministic Wallets" by Das et al. CCS'19](https://dl.acm.org/doi/abs/10.1145/3319535.3354236). For more information about the wallet, head to the wallet repository (linked in /aea_ledger_ethereum_tud).

## Setup
### Requirements
General:
- java (e.g. on Ubuntu via   `sudo apt install default-jre`)

Python (virtual) environment:

- AEA Framework - `pip install aea[all]` (or `pip install "aea[all]"` on zsh)
- eth_accounts - `pip install eth_account`
- eth_utils - `pip install eth_utils`
- jpype - `pip install jpype1`

### Installation
1. Clone this repository including the tudwallet submodule 
``` bash
git clone --recurse-submodules git@github.com:leandro-ro/aea-ledger-ethereum-tud.git
```
2. cd in this repository
``` bash
cd aea-ledger-ethereum-tud
```
3. Install the plugin (Make sure to do this from the same python environment you are using the aea framework with)
``` bash
python setup.py install
```
4. Check in python if plugin appears in aea's crypto_registry
``` python
from aea.crypto.registries import crypto_registry
print(crypto_registry.supported_ids) # Expected: {'tudwallet'}
```
If the print returns `{'tudwallet'}` the plugin has been successfully installed.

## Usage Examples and Explanation
### Wallet initialization
Usually, you get crypto plugins by calling `aea.crypto.registries.make_crypto`, but this returns the wallet object without a type hint. To use autocompletion in your IDE we suggest using this code snippet for constructing the `EthereumTudWallet` object. (If you don't care you can, of course, only call `aea.crypto.registries.make_crypto` to create an instance of the wallet.)

``` python
import aea_ledger_ethereum_tud
from aea.crypto.registries import make_crypto

# Use this wrapper if you want to use autocomplete for EthereumTudWallet inside your IDE
def create_tudwallet(hot_wallet_path: str, cold_wallet_path: str, enable_overwrite=False) -> aea_ledger_ethereum_tud.EthereumTudWallet:
    return make_crypto("tudwallet", hot_wallet_path=hot_wallet_path, cold_wallet_path=cold_wallet_path, enable_overwrite=enable_overwrite)


tudwallet = create_tudwallet(hot_wallet_path="tudwallet/keystore/hot_keystore/",
                          cold_wallet_path="tudwallet/keystore/cold_keystore/")
```
`hot_wallet_path` sets the storage location for all data concerning the hot wallet and `cold_wallet_path` for all data concerning the cold wallet. 

If a hot/cold wallet exists in the given location, the wallet is loaded into the object. If the location is empty (or not existing), the Keystore is created, and a new master key pair is generated.

If you load an existing wallet but want to overwrite the Keystore, set `enable_overwrite` to true. This disables the overwrite protection and gives the opportunity to re-initialize the wallet with `.perform_overwrite()`. If the next call to the wallet object happens to be another method, the overwrite protection is enabled again for safety reasons.
``` python
tudwallet = create_tudwallet(hot_wallet_path="some/existing/hot_wallet/",
                          cold_wallet_path="some/existing/cold_wallet/", enable_overwrite=True)

tudwallet.perform_overwrite() # Wallet deleted and re-initialized with new master key pair
```
Caution: With `.perform_overwrite()`, the master key pair and all derived keys are deleted and cannot be recovered. This could lead to a loss of funds!

### Key derivation
The public and the secret part of each key pair are derived separately, and it is advised to derive the secret part only when needed to keep the interaction with the cold wallet low. Keys can be derived (and are later identified, e.g., for signing) with a unique ID. 

`.public_key(derivation_id: int)` derives a new public key. If the derivation_id had already been used for deriving a public key earlier, the respective public key is returned from the Keystore. If you want to derive a new public key, make sure to use a derivation_id that is higher than all previously used ones. Otherwise, an exception will be raised. The public key is returned as a hex string.

`.private_key(derivation_id: int)` derives a new private key. If the derivation_id had already been used for deriving a private key earlier, the respective private key is returned from the Keystore. If you want to derive a new private key, make sure that a public key with the same derivation_id has been created earlier. Otherwise, an exception will be raised. The private key is returned as a hex string.

`.derivation_ids()` returns a list of all ids used to derive public keys. Therefore, these ids are can be used to produce the respective private keys.

```python
tudwallet.public_key(derivation_id=1)
tudwallet.public_key(derivation_id=2)
tudwallet.public_key(derivation_id=5)  # 5 is now highest id

tudwallet.public_key(derivation_id=2)  # Returns (earlier derived) key from keystore

try:
    # Results in an exception because id 4 not previously derived and 4 < 5
    tudwallet.public_key(derivation_id=4)
except Exception:
    pass

tudwallet.derivation_ids() # returns [1, 2, 5]
tudwallet.private_key(derivation_id=1)  # Secret key for public key with id=1
```

`.address(derivation_id: int)` returns the ethereum address of an already derived public key.

### Message signing
To sign a message use `.sign_message()`. The derivation_id specifies which (already derived!) key pair is being used for signing. An exception will be raised if a derivation_id is given that was not used to derive a public and secret key earlier.
```python
message = "This is a test!"
message_signature = tudwallet.sign_message(message=message, derivation_id=1)
```
The signature is given as hex string.

### Transaction signing
To sign a transaction use `.sign_transaction()`. The derivation_id specifies which (already derived!) key pair is being used for signing. If an derivation_id is given that was not used to derive a public and secret key earlier, an exception will be raised.
```python
transaction = {
    # Note that the address must be in checksum format or native bytes:
    'to': '0x82fc853256B05029b3759161B32E3460Fe4eaC77',
    'value': 10000000000000000,
    'gas': 2000000,
    'gasPrice': 2500000008,
    'nonce': 1, 
    'chainId': 3,  # Ropsten Testnet ID = 3
}

signed_transaction = tudwallet.sign_transaction(transaction_dict=transaction, derivation_id=1)
```
The signed transaction is given as dict, which contains the `rawTransaction`, which can be used to publish the transaction to the ethereum network, the transaction `hash`, and the raw ECDSA signature as `r`, `s`, `v`.
