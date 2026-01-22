from collections import defaultdict
import json
import os

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

def choose_json_file():
    print("\n📂 Select file to count:")
    print("1. Default: manga/all.json")
    print("2. Choose from output/ folder")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        return "manga/all.json"

    # List all .json files in output/, sorted by modification time
    files = sorted(
        [f for f in os.listdir("output") if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join("output", f)),
        reverse=True
    )

    if not files:
        print("❌ No JSON files found in output/")
        exit(1)

    print("\n📄 Available files in output/:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    try:
        selection = int(input("Enter file number to use: ").strip())
        if 1 <= selection <= len(files):
            return os.path.join("output", files[selection - 1])
    except ValueError:
        pass

    print("❌ Invalid selection.")
    exit(1)

def process_raw_backup(backup_data):
    # Build category map from backupCategories
    category_map = {}
    for i, cat in enumerate(backup_data.get("backupCategories", [])):
        key = str(cat.get("order", i))
        category_map[key] = cat.get("name", "Uncategorized")

    # Build source map from backupSources
    source_map = {}
    for src in backup_data.get("backupSources", []):
        source_map[str(src.get("sourceId"))] = src.get("name", "Unknown")

    # Process manga entries
    result = []
    for manga in backup_data.get("backupManga", []):
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
    
    return result

def main():
    emoji_map = load_emoji_map()
    input_file = choose_json_file()

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Process raw backup files differently
    if isinstance(data, dict) and "backupManga" in data:
        data = process_raw_backup(data)
    elif isinstance(data, dict) and "backupManga" in data.get("data", {}):
        # Handle special case where backup is wrapped in "data" key
        data = process_raw_backup(data["data"])

    if not isinstance(data, list) or not all(isinstance(m, dict) for m in data):
        print("❌ JSON structure invalid: expected list of manga dicts.")
        exit(1)

    total = len(data)
    fully_read = sum(1 for m in data if m.get("read_chapters", 0) == m.get("total_chapters", 0) and m.get("total_chapters", 0) > 0)
    unread = sum(1 for m in data if m.get("read_chapters", 0) == 0)
    partial = total - fully_read - unread

    print(f"\n📚 Total manga: {total}")
    print(f"✅ Fully read: {fully_read}")
    print(f"📖 Partially read: {partial}")
    print(f"❌ Unread: {unread}")

    # Extension stats
    extension_count = defaultdict(int)
    for m in data:
        ext = m.get("extension", "Unknown")
        extension_count[ext] += 1

    major_extensions = {ext: count for ext, count in extension_count.items() if count >= 10}
    minor_extensions = {ext: count for ext, count in extension_count.items() if count < 10}

    print("\n📦 Manga per extension (sorted A–Z):")
    for ext in sorted(major_extensions):
        emoji = emoji_map.get(ext, "•")
        print(f"{emoji} {ext}: {major_extensions[ext]}")

    if minor_extensions:
        minor_names = ", ".join(sorted(minor_extensions.keys()))
        minor_total = sum(minor_extensions.values())
        print(f"• Other ({minor_names}): {minor_total}")

    # Category stats
    category_count = defaultdict(int)
    for m in data:
        for cat in m.get("categories", ["Uncategorized"]):
            category_count[cat] += 1

    print("\n🗂️ Manga per category (sorted A–Z):")
    for cat in sorted(category_count):
        emoji = emoji_map.get(cat, "•")
        print(f"{emoji} {cat}: {category_count[cat]}")

if __name__ == "__main__":
    main()