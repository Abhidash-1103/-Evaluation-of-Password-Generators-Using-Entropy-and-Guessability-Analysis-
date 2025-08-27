# Project_Analysis_Code_Report.py
import pandas as pd
import glob, os, math
from collections import Counter
from zxcvbn import zxcvbn

# --- Parameters ---
INPUT_DIR = "."   # current folder
RAW_OUT = "raw_all.csv"
SUMMARY_OUT = "summary_by_group.csv"

# --- Helper: Shannon entropy ---
def shannon_entropy(password):
    if not password:
        return 0
    counts = Counter(password)
    length = len(password)
    return -sum((count/length) * math.log2(count/length) for count in counts.values())

# --- Collect CSV files (only 45 generator files) ---
files = [f for f in glob.glob(os.path.join(INPUT_DIR, "*.csv"))
         if os.path.basename(f).startswith(("pw_", "rb_", "samples_"))]

print(f"Found {len(files)} files to process…")

all_rows = []

# --- Process each file ---
for f in files:
    print(f"[+] Processing {os.path.basename(f)} …")
    df = pd.read_csv(f)

    # Ensure required columns
    if not {"password", "generator", "char_class", "length"}.issubset(df.columns):
        print(f"  Skipped {f}, missing required columns.")
        continue

    # Compute metrics
    metrics = []
    for _, row in df.iterrows():
        pwd = str(row["password"])
        gen = row["generator"]
        cclass = row["char_class"]
        length = row["length"]

        # Shannon entropy
        entropy = shannon_entropy(pwd)

        # zxcvbn
        res = zxcvbn(pwd)
        score = res["score"]
        guesses_log10 = res["guesses_log10"]
        crack_time = res["crack_times_seconds"]["offline_fast_hashing_1e10_per_second"]

        weak = 1 if score < 3 else 0

        metrics.append({
            "password": pwd,
            "generator": gen,
            "char_class": cclass,
            "length": length,
            "entropy": entropy,
            "zxcvbn_score": score,
            "guesses_log10": guesses_log10,
            "crack_time_seconds": crack_time,
            "weak_password": weak
        })

    all_rows.extend(metrics)

# --- Save raw data ---
raw_df = pd.DataFrame(all_rows)
raw_df.to_csv(RAW_OUT, index=False)
print(f"Saved raw row-level data → {RAW_OUT}")

# --- Aggregate summary ---
summary = raw_df.groupby(["generator", "char_class", "length"]).agg(
    avg_entropy=("entropy", "mean"),
    avg_zxcvbn=("zxcvbn_score", "mean"),
    avg_guesses_log10=("guesses_log10", "mean"),
    avg_crack_time=("crack_time_seconds", "mean"),
    weak_pct=("weak_password", "mean"),  # fraction of weak pw
    sample_size=("password", "count")
).reset_index()

summary.to_csv(SUMMARY_OUT, index=False)
print(f"Saved summary stats → {SUMMARY_OUT}")
