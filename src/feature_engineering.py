def extract_features_from_transactions(wallet, transactions):
    """
    Extract risk relevant features for a single wallet from transactions list.
    Example features based on your protocol actions and risk scoring logic.
    """

    # Initialize feature values
    total_deposit_usd = 0.0
    total_borrow_usd = 0.0
    borrow_count = 0
    repay_count = 0
    liquidation_count = 0
    collateral_assets = set()
    timestamps_liquidation = []

    # Process each tx according to known actions
    for tx in transactions:
        action = tx.get('action')
        action_data = tx.get('actionData', {})
        asset_symbol = action_data.get('assetSymbol', '')
        amount_raw = action_data.get('amount', '0')
        price_usd = float(action_data.get('assetPriceUSD', '0'))

        # Some amounts may be in smallest units, make sure to handle properly for real code
        # Here, assuming amount is integer string of token units with decimals:
        # For USDC and similar: 6 decimals => divide by 1e6, else approximate

        amount = float(amount_raw) / 1e6 if asset_symbol in ['USDC', 'USDT', 'DAI'] else float(amount_raw)

        usd_value = amount * price_usd

        if action == 'deposit':
            total_deposit_usd += usd_value
            collateral_assets.add(asset_symbol)
        elif action == 'borrow':
            total_borrow_usd += usd_value
            borrow_count += 1
        elif action == 'repay':
            repay_count += 1
        elif action == 'liquidate' or action == 'liquidation':
            liquidation_count += 1
            timestamps_liquidation.append(tx.get('timestamp', 0))

    # Simple net position
    net_position = total_deposit_usd - total_borrow_usd

    # Loan repayment ratio (if no borrow => 1.0)
    repayment_ratio = (repay_count / borrow_count) if borrow_count > 0 else 1.0

    # Time since last liquidation in seconds relative to current unix time (simplify with example)
    import time
    now = int(time.time())
    if timestamps_liquidation:
        time_since_last_liquidation = now - max(timestamps_liquidation)
    else:
        time_since_last_liquidation = 10**10  # A large number to indicate no liquidation

    # Collateral diversity
    collateral_diversity = len(collateral_assets)

    # Placeholder for average health factor (not available in simple tx data)
    average_health_factor = 1.0  # Assume safe default

    # Position size volatility: simplified: zero because no historic time series here
    position_size_volatility = 0.0

    return {
        'wallet': wallet,
        'total_lifetime_borrow': total_borrow_usd,
        'total_lifetime_supply': total_deposit_usd,
        'net_position': net_position,
        'borrow_frequency': borrow_count,
        'repayment_ratio': repayment_ratio,
        'liquidation_count': liquidation_count,
        'average_health_factor': average_health_factor,
        'time_since_last_liquidation': time_since_last_liquidation,
        'collateral_diversity': collateral_diversity,
        'position_size_volatility': position_size_volatility,
    }
