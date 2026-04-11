import os
from pathlib import Path

# Extract correct persistent user AppData pathway gracefully (compatible across Windows limits).
appdata_env = os.environ.get("APPDATA") or str(Path.home())

# Lock down an absolute directory space explicitly for the application components
APP_DATA_DIR = Path(appdata_env) / "PharmaDistributors"

# Silently authorize creation of directory tree upon logic load if it is a fresh install
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
