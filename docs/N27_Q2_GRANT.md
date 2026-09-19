# N2.7 Q2 grant status

Grant: run-n27-kraken-trades-agg-q2-v1 for 10 pairs, 2026-04-01Z → 2026-06-30Z.
Source: kraken.trades.agg.1h. Not OHLCVT ZIP.
N3 not authorized. complete_archive=0.

Runner: research_db/ingest/q2_runner.py (restartable watermark).
This pass did not persist the full 10×2184 hour cube: Kraken last-id pagination can jump; long jobs were cut by ephemeral /tmp and artifact disk I/O.
Live path remains proven on LTC 3h (N27_PROOF) and partial ADA paging.

Resume on a stable disk: python -c "from pathlib import Path; from research_db.ingest.q2_runner import PAIRS, run_pair; db=Path('q2_bars.sqlite');\n[print(run_pair(p, db)) for p in PAIRS]"
