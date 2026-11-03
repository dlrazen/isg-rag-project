
import json
from pathlib import Path
from statistics import mean

CHUNKS_DIR = Path("data/chunks/size_1000_overlap_100")

all_sizes = []
total_passages = 0
short_passages = 0
long_passages = 0

for file_path in sorted(CHUNKS_DIR.glob("*.json")):

    with open(file_path, "r", encoding="utf-8") as file:
        passages = json.load(file)

    sizes = [p["character_count"] for p in passages]

    if not sizes:
        continue

    total_passages += len(sizes)
    all_sizes.extend(sizes)

    short_passages += sum(s < 200 for s in sizes)
    long_passages += sum(s > 1000 for s in sizes)

    print(f"\n{file_path.stem}")
    print(f"Passages: {len(sizes)}")
    print(f"Average: {mean(sizes):.0f}")
    print(f"Minimum: {min(sizes)}")
    print(f"Maximum: {max(sizes)}")
    print(f"Below 200: {sum(s < 200 for s in sizes)}")
    print(f"Above 1000: {sum(s > 1000 for s in sizes)}")

print("\n========== OVERALL ==========")
print("Total passages:", total_passages)
print("Average size:", round(mean(all_sizes), 2))
print("Minimum size:", min(all_sizes))
print("Maximum size:", max(all_sizes))
print("Below 200 characters:", short_passages)
print("Above 1000 characters:", long_passages)
