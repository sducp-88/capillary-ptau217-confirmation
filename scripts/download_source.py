from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
ROOT = Path(__file__).resolve().parents[1]
URL = "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41591-025-04080-0/MediaObjects/41591_2025_4080_MOESM3_ESM.xlsx"
EXPECTED = "4b1f5983b8548d4f4f5edc08f4b541358ade1d624d0d1d8aaaf44535e89f092b"
target = ROOT / "evidence/source/T030_41591_2025_4080_MOESM3_ESM.xlsx"
data = urlopen(Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
if hashlib.sha256(data).hexdigest() != EXPECTED:
    raise RuntimeError("Source checksum differs from the frozen analysis input; no file was written.")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(data)
print("Official source downloaded and SHA-256 verified.")
