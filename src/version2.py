from PIL import Image, ImageOps
import easyocr
import base64, requests, os, re, warnings, csv, json
from urllib.parse import quote_plus
from datetime import datetime, timezone

# ---- quiet Torch + EasyOCR noise ----
warnings.filterwarnings("ignore", message=".*pin_memory.*")
os.environ["KMP_WARNINGS"] = "0"

try:
    import torch
    GPU_AVAILABLE = bool(getattr(torch, "cuda", None) and torch.cuda.is_available()) \
                    or bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
except Exception:
    GPU_AVAILABLE = False

# ---- config ----
HOST = "149.202.87.35:27015"
START = "-1w"
OUT_DIR = "images"
DATA_DIR = os.path.join("docs", "data")
CROP_BOX = (39, 0, 260, 152)
SCALE_FACTOR = 2

def b64_name(name: str) -> str:
    return quote_plus(base64.b64encode(name.encode("utf-8")).decode("ascii"))

def build_url(name: str) -> str:
    return ("https://cache.gametracker.com/images/graphs/player_time.php"
            f"?nameb64={b64_name(name)}&host={HOST}&start={START}")

def download_image(url: str, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    r = requests.get(url, timeout=20, headers={"User-Agent": "GTStatsBot/1.0"})
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def ocr_total_minutes(reader, image_path: str) -> int:
    gray = ImageOps.grayscale(Image.open(image_path)).crop(CROP_BOX)
    resized = gray.resize(
        (gray.width * SCALE_FACTOR, gray.height * SCALE_FACTOR),
        resample=Image.Resampling.LANCZOS
    )
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp_path = os.path.join(OUT_DIR, "inprogress.png")
    resized.save(tmp_path)
    tokens = reader.readtext(tmp_path, detail=0)

    nums = []
    for t in tokens:
        for x in re.findall(r"\d+", str(t)):
            try:
                nums.append(int(x))
            except ValueError:
                pass
    return sum(nums) if nums else 0

def load_admins(path=os.path.join("data", "admins.txt")):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Admin file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_history(path=os.path.join(DATA_DIR, "leaderboard_history.csv")):
    history = {}
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                history[row["name"]] = int(row["minutes"])
    return history

def save_history(history, path=os.path.join(DATA_DIR, "leaderboard_history.csv")):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "minutes"])
        w.writeheader()
        for name, minutes in sorted(history.items(), key=lambda kv: kv[1], reverse=True):
            w.writerow({"name": name, "minutes": minutes})

def main():
    reader = easyocr.Reader(["en"], gpu=GPU_AVAILABLE)
    admins = load_admins()
    history = load_history()

    results = []
    for name in admins:
        url = build_url(name)
        img_path = os.path.join(OUT_DIR, f"{name}.png")
        try:
            download_image(url, img_path)
            minutes = ocr_total_minutes(reader, img_path)
            history[name] = minutes
            results.append({"name": name, "minutes": minutes})
        except Exception as e:
            print(f"Error processing {name}: {e}")

    # Save outputs
    save_history(history)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    weekly_path = os.path.join(DATA_DIR, f"{now}_weekly_results.csv")
    with open(weekly_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "minutes"])
        w.writeheader()
        for row in results:
            w.writerow(row)

    # Also dump JSON
    weekly_json = os.path.join(DATA_DIR, "weekly_results.json")
    with open(weekly_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
