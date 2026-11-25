"""Reusable cleaning pipeline for the mobile-money agent transaction extract."""
import pandas as pd

TXN_TYPES = {"deposit": "Deposit", "withdrawal": "Withdrawal"}
UNKNOWN_COUNTY = "Unknown"
DATE_FORMAT = "%Y-%m-%d"


def clean_agent_data(txns, agents):
    """Clean the raw agent transactions and attach each agent's county.

    Rules applied, in order (each one is recorded in the log):
      1. Uniqueness: keep one row per txn_id. If copies differ, keep the copy whose
         agent_id exists in the agent register, so no valid information is lost.
      2. Consistency: standardise txn_type to exactly "Deposit" or "Withdrawal".
      3. Validity: convert amount to numbers (blank, "N/A" and other text become
         missing; zero or negative amounts are treated as invalid) and convert
         txn_date to datetime (dates written with "/" are accepted).
      4. Outliers: flag amounts outside the IQR fences, calculated on the real
         (non-imputed) amounts. Flagged rows are kept, never deleted.
      5. Completeness: flag missing amounts in amount_imputed, then fill them with the
         median of the real amounts (rounded to whole shillings).
      6. Merge: left-join the agent register on agent_id. Transactions whose agent is
         not in the register are kept and given the county "Unknown".

    Args:
        txns: raw transactions DataFrame (txn_id, agent_id, txn_type, amount, txn_date).
        agents: agent register DataFrame (agent_id, county, ...).

    Returns:
        (clean_df, log): the cleaned DataFrame and a list of plain-English log lines.
    """
    log = []
    out = txns.copy()
    register = agents.copy()
    log.append(f"Started with {len(out)} transaction rows and {len(register)} registered agents")

    # Tidy identifiers so that stray spaces or lower case cannot break matching.
    out["txn_id"] = out["txn_id"].astype("string").str.strip()
    out["agent_id"] = out["agent_id"].astype("string").str.strip().str.upper()
    register["agent_id"] = register["agent_id"].astype("string").str.strip().str.upper()

    # 1. Uniqueness -------------------------------------------------------------
    n_exact = int(txns.duplicated().sum())
    known_agent = out["agent_id"].isin(register["agent_id"])
    ordered = out.assign(_known=known_agent).sort_values("_known", ascending=False,
                                                         kind="stable")
    is_repeat = ordered.duplicated(subset="txn_id", keep="first")
    n_dupes = int(is_repeat.sum())
    out = ordered[~is_repeat].drop(columns="_known").sort_index()
    log.append(
        f"Uniqueness: removed {n_dupes} duplicate txn_id rows ({n_exact} exact copies, plus "
        f"{n_dupes - n_exact} that differed in another column, where the copy with a "
        f"registered agent was kept); {len(out)} rows remain")

    # 2. Consistency: transaction type -----------------------------------------
    original_type = out["txn_type"].astype("string")
    standard_type = original_type.str.strip().str.lower().map(TXN_TYPES)
    n_retyped = int((standard_type.notna() & (standard_type != original_type)).sum())
    n_unmapped = int(standard_type.isna().sum())
    out["txn_type"] = standard_type
    log.append(f"Consistency: standardised {n_retyped} txn_type values to "
               f"{' / '.join(TXN_TYPES.values())}; {n_unmapped} could not be mapped")

    # 3. Validity: amount and date types ---------------------------------------
    amount_text = (out["amount"].astype("string").str.strip()
                   .str.replace(",", "", regex=False))
    amount = pd.to_numeric(amount_text, errors="coerce").astype("float64")
    n_nonpositive = int((amount <= 0).sum())
    amount = amount.where(~(amount <= 0))
    log.append(f"Validity: {int(amount.isna().sum())} amounts are blank, 'N/A' or not a "
               f"valid positive number ({n_nonpositive} zero or negative)")

    date_text = (out["txn_date"].astype("string").str.strip()
                 .str.replace("/", "-", regex=False))
    n_slash = int(out["txn_date"].astype("string").str.contains("/", regex=False).sum())
    out["txn_date"] = pd.to_datetime(date_text, format=DATE_FORMAT, errors="coerce")
    log.append(f"Validity: converted txn_date to datetime ({n_slash} dates used '/' "
               f"separators); {int(out['txn_date'].isna().sum())} dates could not be parsed")

    # 4. Outliers (IQR fences on real amounts) ---------------------------------
    q1, q3 = amount.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    is_outlier = ((amount > upper) | (amount < lower)).fillna(False).astype(bool)
    log.append(f"Outliers: IQR fences are {max(lower, 0):,.0f} to {upper:,.0f}; "
               f"flagged {int(is_outlier.sum())} amounts in is_outlier (none deleted)")
    repeats = amount[is_outlier].value_counts()
    for value, count in repeats[repeats >= 3].items():
        log.append(f"Outliers: the identical value KES {value:,.0f} appears {count} times "
                   f"among the flagged amounts, which is suspicious")

    # 5. Completeness: flag first, then impute ---------------------------------
    amount_imputed = amount.isna()
    median_amount = round(amount.median())
    out["amount"] = amount.fillna(median_amount)
    out["amount_imputed"] = amount_imputed
    out["is_outlier"] = is_outlier
    log.append(f"Completeness: filled {int(amount_imputed.sum())} missing amounts with the "
               f"median of the real amounts (KES {median_amount:,.0f}) and flagged them in "
               f"amount_imputed")

    # 6. Merge with the agent register -----------------------------------------
    rows_before = len(out)
    merged = out.merge(register[["agent_id", "county"]], on="agent_id", how="left",
                       validate="many_to_one", indicator=True)
    n_unknown = int((merged["_merge"] == "left_only").sum())
    merged["county"] = merged["county"].fillna(UNKNOWN_COUNTY)
    log.append(f"Merge: left join kept {len(merged)} of {rows_before} rows; {n_unknown} "
               f"transactions reference an agent that is not in the register and were "
               f"given the county '{UNKNOWN_COUNTY}'")

    clean = merged[["txn_id", "agent_id", "county", "txn_type", "amount", "txn_date",
                    "amount_imputed", "is_outlier"]].reset_index(drop=True)
    return clean, log
