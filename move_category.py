import json
import os
import shutil
from collections import defaultdict

# Configuration
ROTATION_LIMIT = 5
ROTATION_FILE = "output/rotation_counter.txt"
OUTPUT_BASENAME = "output_moved_{}.json"
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

def get_category_id_by_name(categories, category_name):
    """Find category ID by name"""
    for cat in categories:
        if cat.get("name") == category_name:
            return cat.get("order")
    return None

def create_new_category(data, category_name):
    """Create a new category and return its ID"""
    backup_categories = data.get("backupCategories", [])
    
    # Find the next available order ID (convert all to integers first)
    existing_orders = []
    for cat in backup_categories:
        order = cat.get("order")
        if isinstance(order, (int, float)):
            existing_orders.append(int(order))
        elif isinstance(order, str) and order.isdigit():
            existing_orders.append(int(order))
    
    next_order = max(existing_orders) + 1 if existing_orders else 1
    
    new_category = {
        "name": category_name,
        "order": next_order,
        "flags": 0
    }
    
    backup_categories.append(new_category)
    data["backupCategories"] = backup_categories
    
    return next_order

def add_tags_to_manga(manga, tags):
    """Add tags to manga metadata"""
    if "genre" not in manga:
        manga["genre"] = []
    
    # Wrap tags with parentheses
    formatted_tags = [f"({tag})" for tag in tags]
    
    for tag in formatted_tags:
        if tag not in manga["genre"]:
            manga["genre"].append(tag)
    
    return manga

def main():
    # Load data
    with open("output/output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    emoji_map = load_emoji_map()

    # Build category mappings
    category_map = {}
    category_id_to_name = {}
    for cat in data.get("backupCategories", []):
        order = cat.get("order")
        name = cat.get("name", "Uncategorized")
        category_map[str(order)] = name
        category_id_to_name[order] = name

    # Extract manga data and build category counts
    manga_list = []
    category_counts = defaultdict(int)
    
    for manga in data.get("backupManga", []):
        title = manga.get("title", "Unknown Title")
        category_ids = manga.get("categories", [])
        categories = [category_map.get(str(cid), "Uncategorized") for cid in category_ids] if category_ids else ["Uncategorized"]

        manga_list.append({
            "raw_data": manga,
            "title": title,
            "categories": categories,
            "category_ids": category_ids
        })
        
        # Count manga per category
        for cat in categories:
            category_counts[cat] += 1

    # Include "Uncategorized" explicitly
    if any(not m["raw_data"].get("categories") for m in manga_list):
        category_counts["Uncategorized"] += sum(1 for m in manga_list if not m["raw_data"].get("categories"))

    # Sort categories alphabetically
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[0].lower())

    # Display categories with emojis and counts
    print("\n\033[1mAvailable Categories:\033[0m")
    for i, (category, count) in enumerate(sorted_categories, 1):
        emoji = emoji_map.get(category, "•")
        print(f"\033[94m{i:>2}.\033[0m {emoji} {category}: \033[93m{count}\033[0m manga")

    # User selects source categories
    print("\n\033[1mSelect categories to move manga FROM (space-separated numbers):\033[0m")
    selected = input("Enter category numbers: ").split()
    selected_indices = [int(i) for i in selected if i.isdigit()]
    valid_indices = [i for i in selected_indices if 1 <= i <= len(sorted_categories)]
    
    if not valid_indices:
        print("No valid categories selected. Exiting.")
        return

    source_categories = [sorted_categories[i - 1][0] for i in valid_indices]
    print(f"Selected source categories: {', '.join(source_categories)}")

    # Count manga to be moved
    manga_to_move = []
    for manga in manga_list:
        if any(cat in source_categories for cat in manga["categories"]):
            manga_to_move.append(manga)
    
    print(f"\n📊 Found {len(manga_to_move)} manga in selected categories")

    # Destination options
    print("\n\033[1mDestination Options:\033[0m")
    print("1. Move to existing category")
    print("2. Move to new category")
    
    choice = input("\nEnter your choice (1/2): ")
    while choice not in ["1", "2"]:
        print("Invalid choice!")
        choice = input("Enter your choice (1/2): ")

    destination_category_id = None
    destination_category_name = None

    if choice == "1":
        # Show available categories (excluding source categories)
        available_categories = [cat for cat in sorted_categories if cat[0] not in source_categories]
        
        if not available_categories:
            print("No other categories available!")
            return
            
        print("\n\033[1mAvailable Destination Categories:\033[0m")
        for i, (category, count) in enumerate(available_categories, 1):
            emoji = emoji_map.get(category, "•")
            print(f"\033[94m{i:>2}.\033[0m {emoji} {category}: \033[93m{count}\033[0m manga")
        
        dest_choice = input("\nEnter destination category number: ")
        if dest_choice.isdigit() and 1 <= int(dest_choice) <= len(available_categories):
            destination_category_name = available_categories[int(dest_choice) - 1][0]
            # Find category ID
            destination_category_id = get_category_id_by_name(data.get("backupCategories", []), destination_category_name)
            if destination_category_id is None:
                print(f"Error: Could not find ID for category '{destination_category_name}'")
                return
        else:
            print("Invalid category selection!")
            return
            
    else:  # choice == "2"
        destination_category_name = input("\nEnter new category name: ").strip()
        if not destination_category_name:
            print("Category name cannot be empty!")
            return
        
        # Create new category
        destination_category_id = create_new_category(data, destination_category_name)
        print(f"Created new category: {destination_category_name} (ID: {destination_category_id})")

    # Process manga movement
    moved_count = 0
    output_data = data.copy()
    output_data["backupManga"] = []
    
    for manga in data.get("backupManga", []):
        manga_categories = manga.get("categories", [])
        manga_category_names = [category_map.get(str(cid), "Uncategorized") for cid in manga_categories]
        
        # Intersect with source categories
        intersecting_cats = [cat for cat in manga_category_names if cat in source_categories]
        
        if intersecting_cats:
            # Add only the relevant previous categories as tags (with parentheses)
            manga = add_tags_to_manga(manga, intersecting_cats)
            
            # Remove source categories and add destination category
            new_categories = [
                cid for cid in manga_categories 
                if category_map.get(str(cid), "Uncategorized") not in source_categories
            ]
            
            if destination_category_id not in new_categories:
                new_categories.append(destination_category_id)
            
            manga["categories"] = new_categories
            moved_count += 1
        
        output_data["backupManga"].append(manga)

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

    # Show results
    print(f"\n✅ Successfully moved {moved_count} manga")
    print(f"From: {', '.join(source_categories)}")
    print(f"To: {destination_category_name}")
    print(f"📝 Added tags: {', '.join([f'({cat})' for cat in source_categories])}")

    # Convert to TACHIBK
    print(f"\n🔄 Converting to TACHIBK format...")
    os.makedirs(EXPLAIN_DIR, exist_ok=True)
    
    success, tachibk_file = convert_to_tachibk(output_file, EXPLAIN_DIR)
    
    if success:
        print(f"✅ TACHIBK file created: {tachibk_file}")
        print(f"✅ Processing complete! Modified data saved to \033[1m{output_file}\033[0m")
    else:
        print("❌ Failed to convert to TACHIBK format")

if __name__ == "__main__":
    main()