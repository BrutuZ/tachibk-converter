import json
import os
import shutil
from collections import defaultdict

# Configuration
ROTATION_LIMIT = 5
ROTATION_FILE = "output/rotation_counter.txt"
OUTPUT_BASENAME = "output_cleaned_{}.json"
TACHIBK_CONVERTER = "json_to_tachibk.py"
EXPLAIN_DIR = "explain"

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
    if os.path.exists(ROTATION_FILE):
        with open(ROTATION_FILE, "r") as f:
            try:
                counter = int(f.read().strip())
            except ValueError:
                counter = 0
    else:
        counter = 0

    index = (counter % ROTATION_LIMIT) + 1
    output_filename = f"output/{OUTPUT_BASENAME.format(index)}"

    with open(ROTATION_FILE, "w") as f:
        f.write(str(counter + 1))

    return output_filename

def convert_to_tachibk(json_file, output_dir):
    """Convert JSON file to TACHIBK format"""
    output_filename = os.path.join(output_dir, os.path.basename(json_file).replace(".json", ".tachibk"))
    cmd = f"python {TACHIBK_CONVERTER} --input {json_file} --output {output_filename}"
    result = os.system(cmd)
    return result == 0, output_filename

def main():
    # Load data
    with open("output/output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    emoji_map = load_emoji_map()

    # Build mappings
    category_map = {}
    for i, cat in enumerate(data.get("backupCategories", [])):
        key = str(cat.get("order", i))
        category_map[key] = cat.get("name", "Uncategorized")

    source_map = {}
    for src in data.get("backupSources", []):
        source_map[str(src.get("sourceId"))] = src.get("name", "Unknown")

    # Extract manga data with watch status
    manga_list = []
    watched_categories = defaultdict(int)
    
    for manga in data.get("backupManga", []):
        title = manga.get("title", "Unknown Title")
        category_ids = manga.get("categories", [])
        categories = [category_map.get(str(cid), "Uncategorized") for cid in category_ids] if category_ids else ["Uncategorized"]
        source_id = str(manga.get("source", ""))
        extension = source_map.get(source_id, f"Unknown ({source_id})")

        chapters = manga.get("chapters", [])
        total_chapters = len(chapters)
        read_chapters = sum(1 for c in chapters if c.get("read", False))
        is_watched = read_chapters > 0

        manga_list.append({
            "raw_data": manga,
            "title": title,
            "categories": categories,
            "extension": extension,
            "read_chapters": read_chapters,
            "total_chapters": total_chapters,
            "is_watched": is_watched
        })
        
        # Count watched manga per category
        if is_watched:
            for cat in categories:
                watched_categories[cat] += 1

    # Filter categories that have at least one watched manga
    categories_with_watched = {cat: count for cat, count in watched_categories.items() if count > 0}
    
    if not categories_with_watched:
        print("❌ No categories with watched manga found!")
        return

    # Sort categories alphabetically
    sorted_categories = sorted(categories_with_watched.items(), key=lambda x: x[0].lower())

    # Display categories with emojis and counts
    print("\n\033[1mCategories with watched manga:\033[0m")
    for i, (category, count) in enumerate(sorted_categories, 1):
        emoji = emoji_map.get(category, "•")
        print(f"\033[94m{i:>2}.\033[0m {emoji} {category}: \033[93m{count}\033[0m watched manga")

    # User selection
    selected = input("\nEnter category numbers to keep (space-separated): ").split()
    selected_indices = [int(i) for i in selected if i.isdigit()]
    valid_indices = [i for i in selected_indices if 1 <= i <= len(sorted_categories)]
    
    if not valid_indices:
        print("No valid categories selected. Exiting.")
        return

    selected_categories = [sorted_categories[i - 1][0] for i in valid_indices]
    print(f"Selected categories: {', '.join(selected_categories)}")

    # Create new JSON with only watched manga from selected categories
    output_data = data.copy()
    output_data["backupManga"] = []
    
    # Track manga to keep and duplicates
    kept_manga = []
    removed_duplicates = defaultdict(int)
    manga_titles = defaultdict(list)
    
    # First pass: identify all manga and their duplicates
    for manga in manga_list:
        title = manga["title"]
        manga_titles[title].append(manga)
    
    # Second pass: decide which manga to keep
    for title, duplicates in manga_titles.items():
        # Find watched manga in selected categories
        watched_in_selected = [
            m for m in duplicates 
            if m["is_watched"] and any(cat in selected_categories for cat in m["categories"])
        ]
        
        if watched_in_selected:
            # Keep all watched manga from selected categories
            kept_manga.extend(watched_in_selected)
            # Count removed duplicates
            removed_count = len(duplicates) - len(watched_in_selected)
            if removed_count > 0:
                removed_duplicates[title] = removed_count
        else:
            # Keep all manga if none are watched in selected categories
            kept_manga.extend(duplicates)
    
    # Add kept manga to output
    for manga in kept_manga:
        output_data["backupManga"].append(manga["raw_data"])
    
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

    # Show removal statistics
    print(f"\n📊 Removal statistics:")
    print(f"Total manga kept: {len(kept_manga)}")
    print(f"Total duplicates removed: {sum(removed_duplicates.values())}")
    
    if removed_duplicates:
        print("\nRemoved duplicates by title:")
        for title, count in removed_duplicates.items():
            print(f"  - {title}: {count} duplicates removed")
    
    # Convert to TACHIBK and move to explain directory
    print(f"\n🔄 Converting to TACHIBK format...")
    os.makedirs(EXPLAIN_DIR, exist_ok=True)
    
    success, tachibk_file = convert_to_tachibk(output_file, EXPLAIN_DIR)
    
    if success:
        print(f"✅ TACHIBK file created: {tachibk_file}")
        print(f"✅ Processing complete! Cleaned data saved to \033[1m{output_file}\033[0m")
    else:
        print("❌ Failed to convert to TACHIBK format")

if __name__ == "__main__":
    main()