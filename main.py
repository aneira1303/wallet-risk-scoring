import logging
from typing import List, Dict, Any
import requests
import pandas as pd

from src.feature_engineering import extract_features_from_transactions
from src.normalization import normalize_and_score
from src.data_fetcher import load_wallet_ids  # reuse to load wallet list from CSV

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

# Your Covalent API key here - replace with your actual key
COVALENT_API_KEY = 'cqt_rQxV3fDvHdJvhdDFptCmrh37kTQW'

# Covalent chain ID (1=Ethereum, 137=Polygon, etc.)
CHAIN_ID = 137  # Change depending on your target chain


def fetch_wallet_transactions_covalent(wallet_address: str, chain_id: int = CHAIN_ID) -> List[Dict[str, Any]]:
    """
    Fetch wallet ERC20 token transfer transactions using Covalent API.
    Returns a list of transactions.
    """
    url = f"https://api.covalenthq.com/v1/{chain_id}/address/{wallet_address}/transfers_v2/"
    params = {
        'key': COVALENT_API_KEY,
        'page-size': 1000,
        'page-number': 0
    }

    all_txs = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch tx for {wallet_address}: HTTP {response.status_code}")
            break

        data = response.json()
        items = data.get('data', {}).get('items', [])
        if not items:  # no more transactions
            break

        all_txs.extend(items)

        # Check if more pages available
        pagination = data.get('data', {}).get('pagination', {})
        if pagination.get('has_more', False):
            params['page-number'] += 1
        else:
            break

    logging.info(f"Fetched {len(all_txs)} transactions for wallet {wallet_address}")
    return all_txs


def convert_covalent_to_internal_format(wallet: str, covalent_txs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Covalent API token transfer transactions into your pipeline's transaction dict format.

    Example keys:
    - userWallet: str wallet address
    - action: str ('deposit', 'borrow', 'repay', 'liquidate', etc.)
    - actionData: dict with details like amount, assetSymbol, assetPriceUSD
    - timestamp: int unix timestamp
    """
    internal_txs = []
    for tx in covalent_txs:
        direction = tx.get('transfer_type', '')
        token_symbol = tx.get('contract_ticker_symbol', '')
        raw_amount = tx.get('delta', '0')  # signed int string
        decimals = tx.get('contract_decimals', 18)

        block_signed_at = tx.get('block_signed_at')
        try:
            from dateutil import parser
            dt = parser.isoparse(block_signed_at)
            timestamp = int(dt.timestamp())
        except Exception:
            timestamp = 0

        try:
            amount = abs(int(raw_amount)) / (10 ** decimals)
        except Exception:
            amount = 0.0

        # Simplified action inference
        if int(raw_amount) > 0:
            action = 'deposit'  # incoming tokens to wallet
        else:
            action = 'repay'    # outgoing tokens from wallet (example)

        action_data = {
            'amount': str(amount),
            'assetSymbol': token_symbol,
            'assetPriceUSD': '0.0'  # Placeholder for price, extend as needed
        }

        tx_dict = {
            'userWallet': wallet.lower(),
            'action': action,
            'actionData': action_data,
            'timestamp': timestamp
        }
        internal_txs.append(tx_dict)

    return internal_txs


def main() -> None:
    wallet_list_path = "data/raw/Wallet_id.csv"
    output_csv_path = "outputs/wallet_risk_scores.csv"

    logging.info(f"Loading wallet IDs from {wallet_list_path}")
    wallet_ids = load_wallet_ids(wallet_list_path)
    logging.info(f"Loaded {len(wallet_ids)} wallets")

    all_features = []

    for idx, wallet in enumerate(wallet_ids, start=1):
        logging.info(f"[{idx}/{len(wallet_ids)}] Processing wallet: {wallet}")

        try:
            covalent_txs = fetch_wallet_transactions_covalent(wallet, CHAIN_ID)
            transactions = convert_covalent_to_internal_format(wallet, covalent_txs)
        except Exception as e:
            logging.error(f"Error fetching or converting transactions for wallet {wallet}: {e}")
            transactions = []

        if not transactions:
            logging.info(f"No transactions found for wallet {wallet}, using default safe features")
            features = {
                'wallet': wallet,
                'total_lifetime_borrow': 0.0,
                'total_lifetime_supply': 0.0,
                'net_position': 0.0,
                'borrow_frequency': 0,
                'repayment_ratio': 1.0,
                'liquidation_count': 0,
                'average_health_factor': 1.0,
                'time_since_last_liquidation': 10**10,
                'collateral_diversity': 0,
                'position_size_volatility': 0.0,
            }
        else:
            features = extract_features_from_transactions(wallet, transactions)
            if not features:
                logging.warning(f"Feature extraction failed or empty for wallet {wallet}, using default safe features")
                features = {
                    'wallet': wallet,
                    'total_lifetime_borrow': 0.0,
                    'total_lifetime_supply': 0.0,
                    'net_position': 0.0,
                    'borrow_frequency': 0,
                    'repayment_ratio': 1.0,
                    'liquidation_count': 0,
                    'average_health_factor': 1.0,
                    'time_since_last_liquidation': 10**10,
                    'collateral_diversity': 0,
                    'position_size_volatility': 0.0,
                }

        all_features.append(features)

    feature_df = pd.DataFrame(all_features).set_index('wallet')
    logging.info(f"Extracted features for {len(feature_df)} wallets")

    logging.info("Normalizing features and computing risk scores...")
    scores_df = normalize_and_score(feature_df)

    combined_df = feature_df.join(scores_df)
    combined_df.to_csv(output_csv_path)
    logging.info(f"Saved combined features and risk scores to {output_csv_path}")

    print(combined_df.head())


if __name__ == "__main__":
    main()
