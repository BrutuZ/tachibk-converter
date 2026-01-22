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

def find_all_duplicates(manga_list):
    """Find all duplicate manga grouped by title and category"""
    title_groups = defaultdict(list)
    
    for idx, manga in enumerate(manga_list):
        title = manga["title"]
        title_groups[title].append({
            "index": idx,
            "categories": manga["categories"],
            "manga": manga
        })
    
    # Filter only titles with duplicates
    duplicates = {}
    for title, entries in title_groups.items():
        if len(entries) > 1:
            # Group by category
            category_groups = defaultdict(list)
            for entry in entries:
                for category in entry["categories"]:
                    category_groups[category].append(entry)
            
            duplicates[title] = category_groups
    
    return duplicates

def display_duplicates(duplicates, emoji_map):
    """Display all duplicates with category information"""
    if not duplicates:
        print("✅ No duplicates found!")
        return False
    
    print(f"\n\033[1mFound {len(duplicates)} manga with duplicates:\033[0m")
    
    for i, (title, category_groups) in enumerate(duplicates.items(), 1):
        print(f"\n\033[94m{i}. {title}\033[0m")
        print("   Copies across categories:")
        
        for category, entries in category_groups.items():
            emoji = emoji_map.get(category, "•")
            print(f"     {emoji} {category}: {len(entries)} copies")
    
    return True

def get_user_selections_for_all_duplicates(duplicates, emoji_map):
    """Get user selection for which category to keep for each duplicate title"""
    selections = {}
    
    print(f"\n\033[1mSelect which category to keep for each duplicate manga:\033[0m")
    
    for title, category_groups in duplicates.items():
        print(f"\n\033[1m{title}\033[0m")
        
        categories = list(category_groups.keys())
        for j, category in enumerate(categories, 1):
            emoji = emoji_map.get(category, "•")
            count = len(category_groups[category])
            print(f"  {j}. {emoji} {category} ({count} copies)")
        
        print(f"  {len(categories) + 1}. Keep ALL copies (don't remove any)")
        
        while True:
            try:
                choice = input(f"Enter choice (1-{len(categories) + 1}): ")
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(categories) + 1:
                    if choice_num == len(categories) + 1:
                        selections[title] = None  # Keep all
                    else:
                        selected_category = categories[choice_num - 1]
                        selections[title] = selected_category
                    break
                else:
                    print(f"Please enter a number between 1 and {len(categories) + 1}")
            except ValueError:
                print("Please enter a valid number")
    
    return selections

def remove_duplicates_in_single_pass(manga_list, selections):
    """Remove duplicates in a single pass based on user selections"""
    # Create a list of manga to keep
    manga_to_keep = []
    removal_stats = defaultdict(int)
    
    # Group by title first
    title_groups = defaultdict(list)
    for manga in manga_list:
        title_groups[manga["title"]].append(manga)
    
    # Process each title
    for title, entries in title_groups.items():
        if title in selections and selections[title] is not None:
            # User selected a specific category to keep
            selected_category = selections[title]
            kept = 0
            removed = 0
            
            for manga in entries:
                if selected_category in manga["categories"]:
                    manga_to_keep.append(manga["raw_data"])
                    kept += 1
                else:
                    removed += 1
            
            if removed > 0:
                removal_stats[title] = removed
        else:
            # Keep all entries for this title (user chose "Keep ALL")
            for manga in entries:
                manga_to_keep.append(manga["raw_data"])
    
    return manga_to_keep, removal_stats

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

    # Extract manga data
    manga_list = []
    for manga in data.get("backupManga", []):
        title = manga.get("title", "Unknown Title")
        category_ids = manga.get("categories", [])
        categories = [category_map.get(str(cid), "Uncategorized") for cid in category_ids] if category_ids else ["Uncategorized"]

        manga_list.append({
            "raw_data": manga,
            "title": title,
            "categories": categories
        })

    # Find all duplicates
    print("\n\033[1m=== Scanning for duplicates ===\033[0m")
    duplicates = find_all_duplicates(manga_list)
    
    if not duplicates:
        print("✅ No duplicates found! Exiting.")
        return
    
    # Display all duplicates
    display_duplicates(duplicates, emoji_map)
    
    # Get user selections for all duplicates
    selections = get_user_selections_for_all_duplicates(duplicates, emoji_map)
    
    # Remove duplicates in single pass
    kept_manga, removal_stats = remove_duplicates_in_single_pass(manga_list, selections)
    
    # Create final output
    output_data = data.copy()
    output_data["backupManga"] = kept_manga
    
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

    # Show final statistics
    print(f"\n🎯 Final results:")
    print(f"Total manga kept: {len(kept_manga)}")
    print(f"Total duplicates removed: {sum(removal_stats.values())}")
    
    if removal_stats:
        print("\n📊 Removed duplicates by title:")
        for title, count in removal_stats.items():
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