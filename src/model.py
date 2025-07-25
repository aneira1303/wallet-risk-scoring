# This file could be used for advanced/custom risk scoring logic,
# here logic incorporated in normalization.py, so keep this minimal or extend later
def calculate_risk_score(features_normalized, weights):
    risk_score = sum(features_normalized[feat] * w for feat, w in weights.items())
    risk_score = risk_score * 1000  # scale 0-1000
    return round(risk_score, 2)
