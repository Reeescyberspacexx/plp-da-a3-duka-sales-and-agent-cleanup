# Duka Sales Exploration and Agent Network Clean-Up

**Author:** Marion Oduor · PLP Data Analytics 2026 Cohort

## Summary

This repository holds both Week 3 consulting engagements, built with Python, pandas and Excel.

**Engagement 1: Duka Electronics.** The Head of Sales needs answers for the half-year review (January to June 2026). `duka_sales_exploration.ipynb` inspects 1,000 orders, adds derived columns, ranks branches and products, compares weekends with weekdays, finds the best and worst months and exports the Premium online orders from Nairobi and Mombasa. `excel/duka_branch_summary.xlsx` reproduces the branch ranking with SUMIFS, adds a region column with XLOOKUP and includes a PivotTable of revenue by branch and channel; the notebook checks that every Excel total matches pandas.

**Engagement 2: Mobile money agent network.** The regional manager wants to know which agents and counties handle the most deposits and withdrawals, but the legacy transaction extract is unreliable. `agent_cleanup.ipynb` audits the data against the six data-quality dimensions, cleans it with the reusable function `clean_agent_data()` in `cleaning_pipeline.py`, merges it with the agent register, builds the county and weekly summary tables and ends with a Data Quality Report.

### Agent data: before and after

|                                                             | Rows    |
| ----------------------------------------------------------- | ------- |
| Raw transactions (`agent_transactions.csv`)                 | **612** |
| Clean transactions (`outputs/agent_transactions_clean.csv`) | **600** |
| Duplicate transactions removed                              | 12      |

### Duka Executive Summary

- Duka Electronics earned KES 71.8 million from 1,000 orders between 1 January and 29 June 2026.
- Nairobi is the anchor branch with 36.4% of revenue (KES 26.1 million), almost double second-placed Mombasa at 19.5%, and the branch ranking is the same whether measured by revenue or by number of orders.
- Premium products drive the business: Laptops and Tablets alone generate 84.8% of revenue, and Laptops bring in KES 41.5 million even though Tablets sell more units (691 against 639).
- Weekends are not stronger than weekdays once the number of days is considered: weekend days average KES 383,390 in revenue against KES 405,127 on weekdays, while the average order value is almost identical (KES 71,972 versus KES 71,724).
- April was the best month at KES 13.5 million and June the lowest at KES 10.9 million, a 24.0% gap (though June has only 29 days of data), and the 83 Premium online orders from Nairobi and Mombasa are worth KES 10.2 million (14.2% of revenue), a segment worth protecting and growing.

## Repository contents

| Path                                       | What it is                                                                 |
| ------------------------------------------ | -------------------------------------------------------------------------- |
| `generate_data.py`                         | Both dataset generators, unchanged (Duka seed 2026; agent network seed 44) |
| `duka_sales_exploration.ipynb`             | Engagement 1 notebook                                                      |
| `excel/duka_branch_summary.xlsx`           | SUMIFS table, XLOOKUP region column and PivotTable                         |
| `outputs/premium_online_coast_capital.csv` | Premium online orders from Nairobi and Mombasa                             |
| `cleaning_pipeline.py`                     | `clean_agent_data(txns, agents)` returns `(clean_df, log)`                 |
| `agent_cleanup.ipynb`                      | Engagement 2 notebook                                                      |
| `outputs/agent_transactions_clean.csv`     | Cleaned and merged agent transactions                                      |
| `requirements.txt`                         | Python libraries used                                                      |

## How to run

1. Install the libraries: `pip install -r requirements.txt`
2. Regenerate the raw data: `python generate_data.py`. This writes `duka_sales.csv`, `agents.csv` and `agent_transactions.csv`. The raw CSVs are not committed because they can be recreated exactly from the fixed seeds.
3. Open each notebook and choose **Run all** (in Colab: Runtime → Restart session and run all):
   - [Open duka_sales_exploration.ipynb in Colab](https://colab.research.google.com/github/Reeescyberspacexx/plp-da-a3-duka-sales-and-agent-cleanup/blob/main/duka_sales_exploration.ipynb)
   - [Open agent_cleanup.ipynb in Colab](https://colab.research.google.com/github/Reeescyberspacexx/plp-da-a3-duka-sales-and-agent-cleanup/blob/main/agent_cleanup.ipynb)

The first cell of each notebook downloads any missing repository file and runs `generate_data.py` if the CSVs are absent, so the notebooks also work from a fresh Colab session. Opening the Excel workbook needs Excel 2021 or Microsoft 365, because it uses XLOOKUP.
