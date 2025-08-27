#!/usr/bin/env python3
import random
import string
import csv

# ----- PARAMETERS -----
LENGTHS = [8, 12, 20]               # password lengths
TARGET_PER_COMBO = 10000            # number of samples per combination
BATCH = 1000                        # generate in batches to save memory

# Character class definitions
CLASS_SPECS = {
    "letters": string.ascii_lowercase + string.ascii_uppercase,
    "letters+digits": string.ascii_letters + string.digits,
    "letters+symbols": string.ascii_letters + string.punctuation,
    "symbols+digits": string.punctuation + string.digits,
    "all": string.ascii_letters + string.digits + string.punctuation
}

# ----- GENERATOR -----
def generate_batch(length, alphabet, n):
    """Generate a batch of random passwords."""
    return [
        ''.join(random.choice(alphabet) for _ in range(length))
        for _ in range(n)
    ]

# ----- MAIN -----
if __name__ == "__main__":
    for cname, buckets in CLASS_SPECS.items():
        for L in LENGTHS:
            filename = f"samples_local_{cname}_{L}.csv"
            print(f"[LOCAL] Generating → {filename}")
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["password", "generator", "char_class", "length"])
                
                collected = 0
                while collected < TARGET_PER_COMBO:
                    n = min(BATCH, TARGET_PER_COMBO - collected)
                    batch = generate_batch(L, buckets, n)
                    
                    for pwd in batch:
                        writer.writerow([pwd, "local_custom", cname, L])
                    
                    collected += len(batch)
                    if collected % 2000 == 0:
                        print(f"   {collected} generated for {cname}, length={L}")

    print("[+] All sample files created successfully!")
