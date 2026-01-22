import json
import os
from collections import defaultdict

# === Load emoji.txt ===
def load_emoji_map(path="manga/emoji.txt"):
    emoji_map = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, emoji = line.strip().split(":", 1)
                    emoji_map[key.strip()] = emoji.strip()
    return emoji_map

emoji_map = load_emoji_map()

# === Load output.json ===
with open("output/output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# === Build ID maps ===
category_map = {}
for i, cat in enumerate(data.get("backupCategories", [])):
    key = str(cat.get("order", i))
    category_map[key] = cat.get("name", "Uncategorized")

source_map = {}
for src in data.get("backupSources", []):
    source_map[str(src.get("sourceId"))] = src.get("name", "Unknown")

# === Extract manga data ===
result = []
for manga in data.get("backupManga", []):
    title = manga.get("title", "Unknown Title")
    category_ids = manga.get("categories", [])
    categories = [category_map.get(str(cid), "Uncategorized") for cid in category_ids] or ["Uncategorized"]
    source_id = str(manga.get("source", ""))
    extension = source_map.get(source_id, f"Unknown ({source_id})")

    chapters = manga.get("chapters", [])
    total_chapters = len(chapters)
    read_chapters = sum(1 for c in chapters if c.get("read", False))

    result.append({
        "title": title,
        "categories": categories,
        "extension": extension,
        "read_chapters": read_chapters,
        "total_chapters": total_chapters
    })

# === Prepare output directories ===
output_dir = "manga"
sub_dir = os.path.join(output_dir, "sub")
ext_dir = os.path.join(output_dir, "extension")
os.makedirs(sub_dir, exist_ok=True)
os.makedirs(ext_dir, exist_ok=True)

# === Clean sub/ and extension/ folders ===
for folder in [sub_dir, ext_dir]:
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

# === Write all.json ===
with open(os.path.join(output_dir, "all.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# === Write category .txt files ===
category_groups = defaultdict(list)
for entry in result:
    for cat in entry.get("categories", ["Uncategorized"]):
        category_groups[cat].append(entry)

for category, entries in category_groups.items():
    safe_category = category.replace("/", "-").replace("\\", "-")
    emoji = emoji_map.get(category, "•")
    filename = os.path.join(sub_dir, f"{safe_category}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {emoji} {category}\n\n")
        for i, entry in enumerate(entries, start=1):
            tick = " ✅" if entry["read_chapters"] == entry["total_chapters"] and entry["total_chapters"] > 0 else ""
            f.write(f"{i}. {entry['title']} ({entry['total_chapters']}) [{entry['extension']}] {tick}\n")

# === Write extension .txt files ===
extension_groups = defaultdict(list)
for entry in result:
    extension = entry["extension"]
    extension_groups[extension].append(entry)

for extension, entries in extension_groups.items():
    safe_extension = extension.replace("/", "-").replace("\\", "-")
    filename = os.path.join(ext_dir, f"{safe_extension}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 📦 {extension}\n\n")
        for i, entry in enumerate(entries, start=1):
            catlist = ", ".join(f"{emoji_map.get(cat, '•')} {cat}" for cat in entry.get("categories", ["Uncategorized"]))
            tick = " ✅" if entry["read_chapters"] == entry["total_chapters"] and entry["total_chapters"] > 0 else ""
            f.write(f"{i}. {entry['title']} ({entry['total_chapters']}) [{catlist}]{tick}\n")

print("✅ all.json updated with full category + emoji support.")
print("📁 Category text files saved in 'manga/sub/'")
print("📁 Extension text files saved in 'manga/extension/'")