"""One place to bootstrap the Python path so the API can import from bin/.

The `bin/brain-feed.py` core has a hyphen in its filename, so it can only be
loaded via importlib. `brain_feed_items` already handles that dance and caches
the module in sys.modules; we just make sure `bin/` is on the path first.
"""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIN_DIR = REPO_ROOT / "bin"

if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

# Side-effect: registers `brain_feed` in sys.modules via importlib so route
# modules can `import brain_feed` the same way the Tk GUI does.
import brain_feed_items  # noqa: E402, F401
import brain_wiki_data  # noqa: E402, F401
