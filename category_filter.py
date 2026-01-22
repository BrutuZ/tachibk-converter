import json
import os
from collections import defaultdict

ROTATION_LIMIT = 5
ROTATION_FILE = "output/rotation_counter.txt"
OUTPUT_BASENAME = "output_cleaned_{}.json"

def load_emoji_map(path="manga/emoji.txt"):
    emoji_map = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, emoji = line.strip().split(":", 1)
                    emoji_map[key.strip()] = emoji.strip()
    else:
        print("⚠️ emoji.txt not found. Emojis will be skipped.")
    return emoji_map

def get_next_output_filename():
    os.makedirs("output", exist_ok=True)
    # Read rotation count
    if os.path.exists(ROTATION_FILE):
        with open(ROTATION_FILE, "r") as f:
            try:
                counter = int(f.read().strip())
            except ValueError:
                counter = 0
    else:
        counter = 0

    # Determine next file index
    index = (counter % ROTATION_LIMIT) + 1
    output_filename = f"output/{OUTPUT_BASENAME.format(index)}"

    # Save updated counter
    with open(ROTATION_FILE, "w") as f:
        f.write(str(counter + 1))

    return output_filename

# Load data
with open("output/output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

emoji_map = load_emoji_map()

# Build category and source mappings
category_map = {}
for i, cat in enumerate(data.get("backupCategories", [])):
    key = str(cat.get("order", i))
    category_map[key] = cat.get("name", "Uncategorized")

source_map = {}
for src in data.get("backupSources", []):
    source_map[str(src.get("sourceId"))] = src.get("name", "Unknown")

# Extract manga data
manga_list = []
for manga in data.get("backupManga", []):
    title = manga.get("title", "Unknown Title")
    category_ids = manga.get("categories", [])
    categories = [category_map.get(str(cid), "Uncategorized") for cid in category_ids] if category_ids else ["Uncategorized"]
    source_id = str(manga.get("source", ""))
    extension = source_map.get(source_id, f"Unknown ({source_id})")

    chapters = manga.get("chapters", [])
    total_chapters = len(chapters)
    read_chapters = sum(1 for c in chapters if c.get("read", False))

    manga_list.append({
        "raw_data": manga,
        "title": title,
        "categories": categories,
        "extension": extension,
        "read_chapters": read_chapters,
        "total_chapters": total_chapters
    })

# Build category list with counts
category_counts = defaultdict(int)
for manga in manga_list:
    for cat in manga["categories"]:
        category_counts[cat] += 1

# Include "Uncategorized" explicitly if any manga lacks categories
if any(not m["raw_data"].get("categories") for m in manga_list):
    category_counts["Uncategorized"] += sum(1 for m in manga_list if not m["raw_data"].get("categories"))

# Sort categories alphabetically
sorted_categories = sorted(category_counts.items(), key=lambda x: x[0].lower())

# Display categories with emojis and counts
print("\n\033[1mAvailable Categories:\033[0m")
for i, (category, count) in enumerate(sorted_categories, 1):
    emoji = emoji_map.get(category, "•")
    print(f"\033[94m{i:>2}.\033[0m {emoji} {category}: \033[93m{count}\033[0m manga")

# User choice
print("\n\033[1mOptions:\033[0m")
print("\033[92m1. Remove selected categories\033[0m")
print("\033[91m2. Keep only selected categories\033[0m")

choice = input("\nEnter your choice (1/2): ")
while choice not in ["1", "2"]:
    print("Invalid choice!")
    choice = input("Enter your choice (1/2): ")

# Category selection
selected = input("\nEnter category numbers to select (space-separated): ").split()
selected_indices = [int(i) for i in selected if i.isdigit()]
valid_indices = [i for i in selected_indices if 1 <= i <= len(sorted_categories)]
if not valid_indices:
    print("No valid categories selected. Exiting.")
    exit()

selected_categories = [sorted_categories[i - 1][0] for i in valid_indices]

# Create new JSON
output_data = data.copy()
output_data["backupManga"] = []

if choice == "1":
    print("\n\033[92mRemoving selected categories...\033[0m")
    for manga in manga_list:
        raw = manga["raw_data"]
        existing_cat_ids = raw.get("categories", [])
        if not existing_cat_ids:
            if "Uncategorized" in selected_categories:
                continue
        else:
            new_cat_ids = [
                cid for cid in existing_cat_ids
                if category_map.get(str(cid), "Uncategorized") not in selected_categories
            ]
            if not new_cat_ids and "Uncategorized" in selected_categories:
                continue
            raw["categories"] = new_cat_ids
        output_data["backupManga"].append(raw)
else:
    print("\n\033[91mKeeping only selected categories...\033[0m")
    for manga in manga_list:
        raw = manga["raw_data"]
        existing_cat_ids = raw.get("categories", [])
        if not existing_cat_ids:
            if "Uncategorized" not in selected_categories:
                continue
        else:
            new_cat_ids = [
                cid for cid in existing_cat_ids
                if category_map.get(str(cid), "Uncategorized") in selected_categories
            ]
            if not new_cat_ids and "Uncategorized" not in selected_categories:
                continue
            raw["categories"] = new_cat_ids
        output_data["backupManga"].append(raw)

# Clean unused categories
used_cat_ids = set()
for manga in output_data["backupManga"]:
    used_cat_ids.update(manga.get("categories", []))

output_data["backupCategories"] = [
    cat for cat in data.get("backupCategories", [])
    if cat.get("order") in used_cat_ids
]

# Save to rotating output file
output_file = get_next_output_filename()
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Processing complete! Cleaned data saved to \033[1m{output_file}\033[0m")
print(f"Selected categories: {', '.join(selected_categories)}")