# aea-ledger-ethereum-tud

Crypto plug-in for the AEA framework. 

Provides a custom wallet implementation based on "A Formal Treatment of Deterministic Wallets" by Das et al. CCS'19 - https://dl.acm.org/doi/abs/10.1145/3319535.3354236.

## Install
### Requirements
- python env with aea package installed
- java (e.g. on Ubuntu via   `sudo apt install default-jre`)
- eth_accounts - `pip3 install eth_account`
- eth_utils - `pip3 install eth_utils`
- jpype - `pip3 install jpype1`

Two options to add the plugin:
### From source
1. Clone the repository
2. `cd aea-ledger-ethereum-tud`
3.  
``` bash
python setup.py install
```

### From .egg


## Usage

``` python
from aea.crypto.registries import make_crypto
from aea_ledger_ethereum_tud import EthereumTudWallet


# Use this wrapper if you want autocomplete inside your IDE
def create_tudwallet(hot_wallet_path: str, cold_wallet_path: str) -> EthereumTudWallet:
    return make_crypto("tudwallet", hot_wallet_path=hot_wallet_path, cold_wallet_path=cold_wallet_path)


wallet = create_tudwallet(hot_wallet_path="hot_keystore/", cold_wallet_path="cold_keystore/")
```
