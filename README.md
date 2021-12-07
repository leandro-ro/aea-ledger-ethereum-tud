# aea-ledger-ethereum-tud

Crypto plug-in for the AEA framework. 

Provides a custom wallet implementation based on "A Formal Treatment of Deterministic Wallets" by Das et al. CCS'19 - https://dl.acm.org/doi/abs/10.1145/3319535.3354236.

## Install
### Requirements
General:
- java (e.g. on Ubuntu via   `sudo apt install default-jre`)

Python (virtual) environment:

- AEA Framework - `pip install aea[all]` (or `pip install "aea[all]"` on zsh)
- eth_accounts - `pip install eth_account`
- eth_utils - `pip install eth_utils`
- jpype - `pip install jpype1`

### Install from source
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

## Usage
Usually you get crypto plugins by calling `aea.crypto.registries.make_crypto` but this retruns the wallet object without a type hint. To use autocomplete in your IDE we suggest using this code snippet for constructing the `EthereumTudWallet` object.

``` python
import aea_ledger_ethereum_tud
from aea.crypto.registries import make_crypto

# Use this wrapper if you want to use autocomplete for EthereumTudWallet inside your IDE
def create_tudwallet(hot_wallet_path: str, cold_wallet_path: str) -> aea_ledger_ethereum_tud.EthereumTudWallet:
    return make_crypto("tudwallet", hot_wallet_path=hot_wallet_path, cold_wallet_path=cold_wallet_path)


wallet = create_tudwallet(hot_wallet_path="tudwallet/keystore/hot_keystore/",
                          cold_wallet_path="tudwallet/keystore/cold_keystore/")
```
Otherwise you can simply call `aea.crypto.registries.make_crypto`
``` python
from aea.crypto.registries import make_crypto

wallet = make_crypto("tudwallet", hot_wallet_path="hot/keystore/path/", cold_wallet_path="cold/keystore/path/")

```
