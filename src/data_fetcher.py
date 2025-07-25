import pandas as pd
import json

def load_wallet_ids(path):
    df = pd.read_csv(path)
    print("CSV columns:", df.columns)

    # Try common wallet column names
    for col in ['wallet_id', 'wallet_address', 'address', 'userWallet']:
        if col in df.columns:
            return df[col].str.lower().tolist()

    raise ValueError(
        "No recognized wallet column found in CSV. "
        "Please rename to 'wallet' or one of ['wallet_address', 'address', 'userWallet']"
    )

def load_transactions_for_wallet(wallet, tx_file_path):
    """
    Load transactions from a JSON file and filter for the given wallet.
    Assumes the JSON file is a list of transaction dicts similar to user-wallet-transactions.json.
    """
    with open(tx_file_path, 'r') as f:
        tx_list = json.load(f)

    wallet = wallet.lower()
    wallet_txs = [tx for tx in tx_list if tx.get('userWallet', '').lower() == wallet]
    return wallet_txs
