#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2020 Fetch.AI Limited
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

"""Setup script for "aea_ledger_ethereum" package."""
import aea_ledger_ethereum_tud
from setuptools import find_packages, setup

setup(
    name="aea-ledger-ethereum-tud",
    version="0.0.1",
    author="Leandro Rometsch (Wallet Code)",
    license="Apache-2.0",
    description="Python package wrapping a custom hot/cold wallet (tudwallet).",
    packages=find_packages(include=["aea_ledger_ethereum_tud*"]),
    install_requires=[
        "aea>=1.0.0, <2.0.0",
        "eth-account==0.5.2",
        "eth-utils==1.10.0",
        "jpype1==1.3.0",
    ],
    tests_require=["pytest"],
    entry_points={
        "aea.cryptos": ["tudwallet = aea_ledger_ethereum_tud:EthereumTudWallet"],
    },
    package_data={'': ['aea_ledger_ethereum_tud/tudwallet/libs/*']},
    include_package_data=True,
)
