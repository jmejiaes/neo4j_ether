"""BigQuery extraction from `bigquery-public-data.crypto_ethereum` (ADR-0001).

Replaces the per-transaction Etherscan calls (see legacy `etherscan.py`) that made
the paper's ingestion ~4 min/block. Each function pulls a whole block window in a
handful of queries and returns plain row dicts ready for the batched Neo4j writers
in `db/connection.py`.

PARTITION PRUNING (critical for cost — ADR-0007): the public tables are partitioned
by DAY on their timestamp column (`blocks.timestamp`, `*.block_timestamp`), NOT by
block number. Filtering only on `block_number` scans the *entire* table (hundreds of
GB to TB per query — enough to blow the 1 TB/month free tier in a couple of calls).
So we first read the window's time range from the small `blocks` scan, then inject
those timestamps as literal `block_timestamp` bounds so BigQuery reads only the ~1–2
relevant daily partitions.

Design notes:
- **No balance / no block reward** (ADR-0002): unused by every query. Block nodes
  carry only number + time, matching the paper's model §3.1.
- **is_contract is point-in-time**: an address is a contract if it appears in the
  `contracts` table with a creation block <= the window end.
- **Internal transactions** come from `traces`: successful value-transferring
  sub-calls (non-empty trace_address). `sequence_id` is 1-based per parent tx.

Auth: Application Default Credentials + `GCP_PROJECT` in .env.
"""

from google.cloud import bigquery

from ether.config import GCP_PROJECT

_DATASET = "bigquery-public-data.crypto_ethereum"
_WEI = 10 ** 18


def _client() -> bigquery.Client:
    if not GCP_PROJECT:
        raise RuntimeError(
            "GCP_PROJECT is not set in .env. Set it to a Google Cloud project with "
            "the BigQuery API enabled, and authenticate with "
            "`gcloud auth application-default login`."
        )
    return bigquery.Client(project=GCP_PROJECT)


def _query(sql: str, params: dict | None = None) -> list[dict]:
    client = _client()
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(k, "INT64", v) for k, v in (params or {}).items()
        ]
    )
    return [dict(r) for r in client.query(sql, job_config=job_config).result()]


def dry_run_bytes(sql: str, params: dict | None = None) -> int:
    """Estimated bytes scanned WITHOUT running the query (free; no quota use).
    Use to sanity-check that partition pruning is working before a real load.
    """
    client = _client()
    job_config = bigquery.QueryJobConfig(
        dry_run=True,
        use_query_cache=False,
        query_parameters=[
            bigquery.ScalarQueryParameter(k, "INT64", v) for k, v in (params or {}).items()
        ],
    )
    return client.query(sql, job_config=job_config).total_bytes_processed


# --- time range (drives partition pruning) ----------------------------------

def block_time_bounds(start_block: int, end_block: int) -> tuple[str, str]:
    """UTC 'YYYY-MM-DD HH:MM:SS' min/max block timestamps for the range.

    A transaction/trace's `block_timestamp` equals its block's timestamp, so these
    bounds are exact for the window — no padding needed. Scans only the small
    number+timestamp columns of the `blocks` table.
    """
    sql = f"""
    SELECT FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', MIN(timestamp), 'UTC') AS mn,
           FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', MAX(timestamp), 'UTC') AS mx
    FROM `{_DATASET}.blocks`
    WHERE number BETWEEN @start AND @end
    """
    row = _query(sql, {"start": start_block, "end": end_block})[0]
    if not row["mn"]:
        raise ValueError(f"No blocks found in range {start_block}-{end_block}")
    return row["mn"], row["mx"]


def _ts(literal: str) -> str:
    """Format a 'YYYY-MM-DD HH:MM:SS' string as a BigQuery TIMESTAMP literal."""
    return f"TIMESTAMP('{literal}+00')"


# --- Blocks -----------------------------------------------------------------

def fetch_blocks(start_block: int, end_block: int) -> list[dict]:
    """Block rows: {number, time}. `time` formatted like the paper's block_time."""
    sql = f"""
    SELECT number,
           FORMAT_TIMESTAMP('%b-%d-%Y %I:%M:%S %p +UTC', timestamp) AS time
    FROM `{_DATASET}.blocks`
    WHERE number BETWEEN @start AND @end
    ORDER BY number
    """
    return _query(sql, {"start": start_block, "end": end_block})


# --- External transactions --------------------------------------------------

def fetch_transactions(start_block: int, end_block: int, ts0: str, ts1: str) -> list[dict]:
    """External-tx rows: {transactionhash, blocknumber, value, sender, receiver}.

    `ts0`/`ts1` are the window's block-timestamp bounds (from block_time_bounds)
    used to prune partitions. `receiver` falls back to the created contract address,
    then 'undefined' (contract-creation txs have a null `to_address`).
    """
    sql = f"""
    SELECT `hash` AS transactionhash,
           block_number AS blocknumber,
           SAFE_DIVIDE(CAST(value AS FLOAT64), {_WEI}) AS value,
           from_address AS sender,
           COALESCE(to_address, receipt_contract_address, 'undefined') AS receiver
    FROM `{_DATASET}.transactions`
    WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
      AND block_number BETWEEN @start AND @end
    ORDER BY block_number, transaction_index
    """
    return _query(sql, {"start": start_block, "end": end_block})


# --- Internal transactions (traces) -----------------------------------------

def fetch_internal_transactions(start_block: int, end_block: int, ts0: str, ts1: str) -> list[dict]:
    """Internal-tx rows: {parenttransactionhash, sequence_id, amount, sender, receiver}.

    Successful value-transferring sub-calls (non-empty trace_address). sequence_id
    is 1-based per parent transaction, ordered by trace_address — mirroring the
    Etherscan internal-transaction numbering used in the original pipeline.
    """
    sql = f"""
    SELECT transaction_hash AS parenttransactionhash,
           ROW_NUMBER() OVER (
               PARTITION BY transaction_hash
               ORDER BY trace_address
           ) AS sequence_id,
           SAFE_DIVIDE(CAST(value AS FLOAT64), {_WEI}) AS amount,
           from_address AS sender,
           COALESCE(to_address, 'undefined') AS receiver
    FROM `{_DATASET}.traces`
    WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
      AND block_number BETWEEN @start AND @end
      AND trace_type = 'call'
      AND status = 1
      AND trace_address IS NOT NULL
      AND trace_address != ''
      AND value > 0
      AND transaction_hash IS NOT NULL
    ORDER BY parenttransactionhash, sequence_id
    """
    return _query(sql, {"start": start_block, "end": end_block})


# --- Contract detection -----------------------------------------------------

def fetch_contract_addresses(start_block: int, end_block: int, ts0: str, ts1: str) -> set[str]:
    """Addresses that are contracts as of `end_block` (point-in-time is_contract).

    Restricted to addresses appearing in the window's txs/traces. NOTE: the
    `contracts` scan is pruned only on the upper bound (block_timestamp <= ts1), so
    it reads all partitions up to the window end, not just the window's days — a
    cost caveat, not a correctness one. Addresses absent from the `contracts` table
    (precompiles, L2 alias/system addresses) are treated as EOAs; see the
    contract-classification limitation in the paper.
    """
    sql = f"""
    WITH window_addrs AS (
        SELECT from_address AS a FROM `{_DATASET}.transactions`
            WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
              AND block_number BETWEEN @start AND @end
        UNION DISTINCT
        SELECT to_address FROM `{_DATASET}.transactions`
            WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
              AND block_number BETWEEN @start AND @end
        UNION DISTINCT
        -- contracts created in-window (receiver of a creation tx) so they are
        -- classified even if not otherwise referenced in the window
        SELECT receipt_contract_address FROM `{_DATASET}.transactions`
            WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
              AND block_number BETWEEN @start AND @end
              AND receipt_contract_address IS NOT NULL
        UNION DISTINCT
        SELECT from_address FROM `{_DATASET}.traces`
            WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
              AND block_number BETWEEN @start AND @end
        UNION DISTINCT
        SELECT to_address FROM `{_DATASET}.traces`
            WHERE block_timestamp BETWEEN {_ts(ts0)} AND {_ts(ts1)}
              AND block_number BETWEEN @start AND @end
    )
    SELECT DISTINCT c.address AS address
    FROM `{_DATASET}.contracts` c
    JOIN window_addrs w ON w.a = c.address
    WHERE c.block_timestamp <= {_ts(ts1)}
    """
    return {r["address"] for r in _query(sql, {"start": start_block, "end": end_block})}


# --- Verification helper ----------------------------------------------------

def verify_era_dates(eras) -> list[dict]:
    """Return {name, start_block, start_time, end_time} for each era, to confirm
    the approximate block heights in experiments/eras.py map to intended dates.
    """
    out = []
    for e in eras:
        start_rows = fetch_blocks(e.start_block, e.start_block)
        end_rows = fetch_blocks(e.end_block, e.end_block)
        out.append({
            "name": e.name,
            "start_block": e.start_block,
            "start_time": start_rows[0]["time"] if start_rows else None,
            "end_time": end_rows[0]["time"] if end_rows else None,
        })
    return out
