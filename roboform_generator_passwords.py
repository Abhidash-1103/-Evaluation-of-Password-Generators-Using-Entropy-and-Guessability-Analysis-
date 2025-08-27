#!/usr/bin/env python3
import random
import string
import csv
import os

# ✅ Define character sets including the missing "symbols+digits"
charsets = {
    "letters": string.ascii_letters,
    "letters+digits": string.ascii_letters + string.digits,
    "letters+symbols": string.ascii_letters + string.punctuation,
    "symbols+digits": string.digits + string.punctuation,
    "all": string.ascii_letters + string.digits + string.punctuation,
}

# Password lengths to generate
lengths = [8, 12, 20]

# Number of passwords per file
NUM_PASSWORDS = 10000

def generate_passwords(charset, length, count):
    return [
        ''.join(random.choice(charset) for _ in range(length))
        for _ in range(count)
    ]

def save_passwords(filename, passwords, generator, cname, length):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["password", "generator", "char_class", "length"])  # ✅ Full header
        for pwd in passwords:
            writer.writerow([pwd, generator, cname, length])

def main():
    for cname, charset in charsets.items():
        for length in lengths:
            filename = f"rb_{cname}_{length}.csv"
            if os.path.exists(filename):
                print(f"[RoboForm] {cname}/{length}: already exists, skipping.")
                continue
            print(f"[RoboForm] Generating {cname}/{length} ...")
            pwds = generate_passwords(charset, length, NUM_PASSWORDS)
            save_passwords(filename, pwds, "rb", cname, length)  # ✅ Save with metadata
    print("[RoboForm] ✅ Generation complete with metadata!")

if __name__ == "__main__":
    main()
