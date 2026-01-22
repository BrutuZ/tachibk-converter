import json
import os
import shutil
from collections import defaultdict

# Configuration
ROTATION_LIMIT = 5
ROTATION_FILE = "output/rotation_counter.txt"
OUTPUT_BASENAME = "output_source_replaced_{}.json"
TACHIBK_CONVERTER = "json_to_tachibk.py"
EXPLAIN_DIR = "explain"

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

def find_source_details(data, source_id):
    """Find source details by ID"""
    for source in data.get("backupSources", []):
        if str(source.get("sourceId")) == str(source_id):
            return source
    return None

def find_manga_by_source_id(data, source_id):
    """Find all manga from a specific source ID"""
    manga_list = []
    for manga in data.get("backupManga", []):
        if str(manga.get("source")) == str(source_id):
            manga_list.append(manga)
    return manga_list

def analyze_manga_categories(data, manga_list):
    """Analyze categories of manga list"""
    category_map = {}
    for cat in data.get("backupCategories", []):
        category_map[str(cat.get("order"))] = cat.get("name", "Uncategorized")
    
    category_stats = defaultdict(int)
    for manga in manga_list:
        category_ids = manga.get("categories", [])
        for cat_id in category_ids:
            cat_name = category_map.get(str(cat_id), "Uncategorized")
            category_stats[cat_name] += 1
    
    return category_stats, category_map

def display_source_info(source, manga_count, category_stats):
    """Display information about the source"""
    print(f"\n\033[1m📊 Source Information:\033[0m")
    print(f"   Source ID: \033[94m{source.get('sourceId')}\033[0m")
    print(f"   Name: \033[92m{source.get('name', 'Unknown')}\033[0m")
    print(f"   Language: {source.get('lang', 'Unknown')}")
    print(f"   Total manga found: \033[93m{manga_count}\033[0m")
    
    if category_stats:
        print(f"\n\033[1m📂 Category Distribution:\033[0m")
        for category, count in sorted(category_stats.items()):
            print(f"   • {category}: {count} manga")

def get_valid_source_id(prompt, data):
    """Get a valid source ID from user"""
    while True:
        try:
            source_id = input(prompt).strip()
            if not source_id:
                print("❌ Source ID cannot be empty!")
                continue
            
            # Check if source exists
            source = find_source_details(data, source_id)
            if source:
                return source_id, source
            else:
                print(f"❌ Source ID {source_id} not found in backup!")
                print("Available source IDs:")
                for src in data.get("backupSources", []):
                    print(f"  {src.get('sourceId')}: {src.get('name')}")
        except ValueError:
            print("❌ Please enter a valid source ID!")

def main():
    # Load data
    try:
        with open("output/output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ output/output.json not found!")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in output.json!")
        return

    print("🎯 Source ID Replacer")
    print("=" * 50)

    # Get source ID to find
    source_id, source = get_valid_source_id("\n🔍 Enter source ID to find manga from: ", data)
    
    # Find all manga from this source
    manga_list = find_manga_by_source_id(data, source_id)
    
    if not manga_list:
        print(f"❌ No manga found for source ID {source_id}!")
        return
    
    # Analyze categories
    category_stats, category_map = analyze_manga_categories(data, manga_list)
    
    # Display information
    display_source_info(source, len(manga_list), category_stats)
    
    # Get replacement source ID
    print(f"\n\033[1m🔄 Replacement Options:\033[0m")
    new_source_id, new_source = get_valid_source_id("Enter replacement source ID: ", data)
    
    # Confirm replacement
    print(f"\n\033[1m⚠️  Replacement Confirmation:\033[0m")
    print(f"   From: {source.get('name')} (ID: {source_id})")
    print(f"   To: {new_source.get('name')} (ID: {new_source_id})")
    print(f"   Total manga to modify: {len(manga_list)}")
    
    confirm = input("\nConfirm replacement? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Operation cancelled!")
        return

    # Create new data structure with only the modified manga
    new_data = {
        "backupManga": [],
        "backupSources": [new_source],  # Only include the target source
        "backupCategories": data.get("backupCategories", []),
        "backupPreferences": data.get("backupPreferences", []),
        "backupSourcePreferences": data.get("backupSourcePreferences", []),
        "version": data.get("version", 2),
        "backupCreatedAt": data.get("backupCreatedAt", 0)
    }

    # Replace source ID for all manga
    modified_count = 0
    for manga in manga_list:
        # Create a copy of the manga
        new_manga = manga.copy()
        # Replace the source ID
        new_manga["source"] = new_source_id
        new_data["backupManga"].append(new_manga)
        modified_count += 1

    # Clean unused categories
    used_cat_ids = set()
    for manga in new_data["backupManga"]:
        used_cat_ids.update(manga.get("categories", []))

    new_data["backupCategories"] = [
        cat for cat in data.get("backupCategories", [])
        if cat.get("order") in used_cat_ids
    ]

    # Save to rotating output file
    output_file = get_next_output_filename()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Successfully modified {modified_count} manga")
    print(f"   From: {source.get('name')} (ID: {source_id})")
    print(f"   To: {new_source.get('name')} (ID: {new_source_id})")

    # Convert to TACHIBK
    print(f"\n🔄 Converting to TACHIBK format...")
    os.makedirs(EXPLAIN_DIR, exist_ok=True)
    
    success, tachibk_file = convert_to_tachibk(output_file, EXPLAIN_DIR)
    
    if success:
        print(f"✅ TACHIBK file created: {tachibk_file}")
        print(f"✅ JSON file created: {output_file}")
        print(f"📊 Files contain only the {modified_count} modified manga")
    else:
        print("❌ Failed to convert to TACHIBK format")

def show_available_sources(data):
    """Show all available sources"""
    print("\n\033[1m📚 Available Sources:\033[0m")
    for source in data.get("backupSources", []):
        print(f"  {source.get('sourceId')}: {source.get('name')} ({source.get('lang', 'Unknown')})")

if __name__ == "__main__":
    # Load data first
    try:
        with open("output/output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ output/output.json not found!")
        exit(1)
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in output.json!")
        exit(1)

    # Show available sources
    show_available_sources(data)
    
    # Run main function
    main()