"""N2.6 deferred official-archive completion watch. Not continuous ingest."""
from __future__ import annotations
from dataclasses import dataclass
WATCH_CODE = "N2.6.ARCHIVE_WATCH"
WATCH_VERSION = "v1"
MISSING_START = "2026-04-01T00:00:00+00:00"
MISSING_END = "2026-08-05T16:00:00+00:00"
FOLDER_URL = "https://drive.google.com/drive/folders/15RSlNuW_h0kVM8or8McOGOMfHeBFvFGI"
EXPECTED = ("Kraken_OHLCVT_Q2_2026.zip", "Kraken_OHLCVT_Q3_2026.zip")
SNAPSHOT_CODE = "snap-cryptolab10-kraken-1h-v1"

@dataclass(frozen=True)
class ArchiveWatch:
    code: str = WATCH_CODE
    version: str = WATCH_VERSION
    missing_start: str = MISSING_START
    missing_end: str = MISSING_END
    folder_url: str = FOLDER_URL
    expected_files: tuple[str, ...] = EXPECTED
    snapshot_code: str = SNAPSHOT_CODE
    auto_ingest: bool = False
    load_authorized: bool = False
    snapshot_complete: bool = False
    n3_authorized: bool = False
    def load_allowed(self, filename: str) -> bool:
        if self.auto_ingest or not self.load_authorized:
            return False
        return filename in self.expected_files

def default_watch() -> ArchiveWatch:
    return ArchiveWatch()

def classify_probe(names: set[str]) -> dict[str, object]:
    present = [f for f in EXPECTED if f in names]
    absent = [f for f in EXPECTED if f not in names]
    return {"watch": WATCH_CODE, "expected": list(EXPECTED), "present": present, "absent": absent, "gap_closed": absent == [], "auto_ingest": False, "load_authorized": False, "snapshot_complete": False, "n3_authorized": False, "missing_interval": f"{MISSING_START} → {MISSING_END}"}
