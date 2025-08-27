# fetch_passwordwolf_resumable.py
import csv, time, os, requests, itertools

LENGTHS = [8, 12, 20]
CLASS_MAP = {
    "letters":          dict(upper=True,  lower=True,  numbers=False, special=False),
    "letters+digits":   dict(upper=True,  lower=True,  numbers=True,  special=False),
    "letters+symbols":  dict(upper=True,  lower=True,  numbers=False, special=True),
    "symbols+digits":   dict(upper=False, lower=False, numbers=True,  special=True),
    "all":              dict(upper=True,  lower=True,  numbers=True,  special=True),
}
TARGET_PER_COMBO = 10_000
URL = "https://passwordwolf.com/api/"

def combo_path(cname, L):
    return f"pw_wolf_{cname}_{L}.csv"

def existing_count(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        # subtract header if present
        return max(0, sum(1 for _ in f) - 1)

def get_one(session, length, params, timeout=12):
    p = {"length": length, **params}
    r = session.get(URL, params=p, timeout=timeout)
    r.raise_for_status()
    return r.json()[0]["password"]

with requests.Session() as sess:
    sess.headers.update({"User-Agent": "pw-research/1.0"})
    for cname, params in CLASS_MAP.items():
        for L in LENGTHS:
            path = combo_path(cname, L)
            need = TARGET_PER_COMBO - existing_count(path)
            if need <= 0:
                print(f"[Wolf] {cname}/{L}: already complete.")
                continue
            print(f"[Wolf] {cname}/{L}: need {need} more …")
            # open append, write header if new
            new_file = not os.path.exists(path)
            with open(path, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if new_file:
                    w.writerow(["password", "generator", "char_class", "length"])
                collected = 0
                backoff = 0.5
                while collected < need:
                    try:
                        pwd = get_one(sess, L, params)
                        w.writerow([pwd, "passwordwolf", cname, L])
                        collected += 1
                        if collected % 1000 == 0:
                            print("  ", collected, "…")
                        time.sleep(0.1)  # be gentle to reduce timeouts
                        backoff = 0.5   # reset backoff after success
                    except Exception as e:
                        print("   retry:", e)
                        time.sleep(backoff)
                        backoff = min(backoff * 1.7, 8.0)

# merge per-combo into one file
out = "samples_passwordwolf.csv"
with open(out, "w", newline="", encoding="utf-8") as fout:
    wout = csv.writer(fout)
    wout.writerow(["password", "generator", "char_class", "length"])
    for cname in CLASS_MAP:
        for L in LENGTHS:
            path = f"pw_wolf_{cname}_{L}.csv"
            with open(path, "r", encoding="utf-8") as fin:
                next(fin)  # skip header
                for line in fin:
                    fout.write(line)
print("Done → samples_passwordwolf.csv")