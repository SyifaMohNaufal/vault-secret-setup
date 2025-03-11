# Vault Secret Setup

## Overview
This repository contains a script to automate the creation of Vault secrets. The script performs the following tasks:
- Creates a Vault secret engine (mount).
- Adds secret data.
- Defines policies.
- Sets up an AppRole authentication method.
- Generates Role ID and Secret ID.
- Reads input data from `vault_input.xlsx`.
- Stores the generated Vault credentials in `vault_output.xlsx`.

## Prerequisites
Ensure you have the following installed before proceeding:
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs/install)
- Python 3.x
- `pip` (Python package manager)
- `virtualenv` (for environment isolation)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/SyifaMohNaufal/vault-secret-setup.git
cd vault-secret-setup
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv  # Create a virtual environment
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare Input Data
Edit `vault_input.xlsx` with the necessary details before running the script.

### 2. Run the Script
```bash
python vault_setup.py
```

### 3. Output
After execution, the generated Vault credentials will be stored in `vault_output.xlsx`.

## License
This project is licensed under the MIT License.

## Author
[Syifa Mohammad Naufal](https://github.com/SyifaMohNaufal)

