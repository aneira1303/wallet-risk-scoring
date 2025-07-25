 Wallet Risk Scoring System

## Overview

This project implements a comprehensive pipeline to assess financial risk scores of blockchain wallets based on their DeFi transaction histories. By analyzing wallet activities—such as deposits, borrows, and liquidations—across protocols like Aave V2 and Compound V2/V3, it derives risk indicators helping institutions and developers evaluate wallet reliability.

Key features:

- Dynamic transaction data fetching via **Covalent API**, supporting multiple chains (e.g., Polygon, Ethereum).
- Extraction of detailed behavior features including borrow/supply amounts, liquidation events, repayment ratios, and position volatility.
- Score normalization and weighted aggregation into interpretable risk scores (0 to 1000 scale).
- Extensive visualization support — distributions, correlations, scatter plots, boxplots, pairplots, and ranking charts.
- Modular, extensible design for adapting to new data sources or risk factors.

-To Start the Project

python main.py

This will fetch transactions automatically from Covalent for each wallet, extract risk features, compute risk scores, and save results in `outputs/wallet_risk_scores.csv`.

-Run all - To run the cells in jupyter notebook

jupyter notebook risk_scoring_analysis.ipynb


 Features Extracted

The system extracts multiple quantitative risk-related features per wallet, including but not limited to:

- **Total Lifetime Borrowed:** Aggregate amount borrowed by the wallet.
- **Total Lifetime Supplied:** Aggregate amount supplied/deposited.
- **Net Position:** Net exposure calculated from borrow and supply.
- **Borrow Frequency:** Count or rate of borrow actions.
- **Repayment Ratio:** Proportion of borrow repaid on time.
- **Liquidation Count:** Number of liquidation events affecting the wallet.
- **Average Health Factor:** Average health factor (protocol-specific financial health indicator).
- **Time Since Last Liquidation:** Time duration since last liquidation event.
- **Collateral Diversity:** Variety of collateral types deposited.
- **Position Size Volatility:** Variability in position sizes over time.

These features serve as inputs to the normalization and weighted scoring model producing a single risk score per wallet.



  Visualization Outputs

- **Risk Score Distribution:** Histogram + KDE showing risk population distribution.
- **Feature Correlation Heatmap:** Visualizes predictive patterns between features.
- **Scatter Plots:** Relations of risk with liquidation count and borrow frequency.
- **Boxplots:** Distributions of key features split by risk categories (low, medium, high).
- **Pairplots:** Multivariate exploration of features by risk class.
- **Top Risk Wallets:** Ranked bar chart focused on highest risk wallets for scrutiny.

All plot images are saved in `outputs/` folder in PNG format, ready for reporting or presentations.



  Best Practices & Notes

- **API Usage:** Covalent API free tier has rate limits; cache results or batch requests accordingly.
- **Data Quality:** Ensure wallets correspond to the correct blockchain network; inconsistencies may lead to missing transactions.
- **Security:** Never hardcode API keys in public repos; consider environment variables for production use.
- **Extensibility:** Easily add additional feature extraction logic or integrate alternative data sources.
- **Error Handling:** Default safe features are applied for wallets with no available transactions to maintain scoring continuity.
- **Dependencies:** See `requirements.txt` for exact package versions.
