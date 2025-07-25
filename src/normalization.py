import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def normalize_and_score(features_df):
    weights = {
        'liquidation_count': 0.30,
        'average_health_factor': 0.20,
        'repayment_ratio': 0.15,
        'borrow_frequency': 0.10,
        'net_position': 0.10,
        'time_since_last_liquidation': 0.05,
        'collateral_diversity': 0.05,
        'position_size_volatility': 0.05,
    }

    feature_cols = list(weights.keys())
    df = features_df.copy()

    # Fill missing with 0
    df = df.fillna(0)

    scaler = MinMaxScaler()
    normalized_vals = scaler.fit_transform(df[feature_cols])
    normalized_df = pd.DataFrame(normalized_vals, columns=feature_cols, index=df.index)

    # Invert safe features (higher = safer)
    for col in ['repayment_ratio', 'net_position', 'time_since_last_liquidation', 'collateral_diversity']:
        normalized_df[col] = 1 - normalized_df[col]

    # Weighted risk factor
    risk_factor = 0
    for feat, w in weights.items():
        risk_factor += normalized_df[feat] * w

    normalized_df['risk_score'] = (risk_factor * 1000).round(2)
    return normalized_df[['risk_score']]
