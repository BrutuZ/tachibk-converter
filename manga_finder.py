import json
from collections import defaultdict

def load_emoji_map(path="manga/emoji.txt"):
    """Load emoji mappings from file"""
    emoji_map = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, emoji = line.strip().split(":", 1)
                    emoji_map[key.strip()] = emoji.strip()
    except FileNotFoundError:
        print("⚠️ emoji.txt not found. Emojis will be skipped.")
    return emoji_map

def load_manga_data():
    """Load and process manga data from output.json"""
    try:
        with open("output/output.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ output/output.json not found!")
        return None, None, None
    
    # Build category mappings
    category_map = {}
    for cat in data.get("backupCategories", []):
        order = cat.get("order")
        name = cat.get("name", "Uncategorized")
        category_map[str(order)] = name
    
    # Build manga list with categories
    manga_list = []
    for manga in data.get("backupManga", []):
        title = manga.get("title", "Unknown Title")
        category_ids = manga.get("categories", [])
        categories = [category_map.get(str(cid), "Uncategorized") for cid in category_ids] 
        if not categories:
            categories = ["Uncategorized"]
        
        manga_list.append({
            "title": title,
            "categories": categories,
            "raw_data": manga
        })
    
    return manga_list, category_map, data

def search_manga(manga_list, search_term):
    """Search for manga by title (case-insensitive, partial match)"""
    results = []
    search_lower = search_term.lower()
    
    for manga in manga_list:
        title_lower = manga["title"].lower()
        if search_lower in title_lower:
            results.append(manga)
    
    return results

def display_results(results, emoji_map):
    """Display search results with colored output"""
    if not results:
        print("❌ No manga found matching your search.")
        return
    
    print(f"\n🔍 Found {len(results)} manga matching your search:\n")
    
    for i, manga in enumerate(results, 1):
        title = manga["title"]
        categories = manga["categories"]
        
        # Format title in dark blue
        title_formatted = f"\033[94m{title}\033[0m"
        
        # Format categories in medium green with emojis
        category_strings = []
        for cat in categories:
            emoji = emoji_map.get(cat, "•")
            category_strings.append(f"\033[92m{emoji} {cat}\033[0m")
        
        categories_formatted = ", ".join(category_strings)
        
        print(f"{i:>2}. {title_formatted}")
        print(f"    📂 Categories: {categories_formatted}\n")

def main():
    """Main function to run the manga finder"""
    print("🎯 Manga Finder - Search for manga by name")
    print("=" * 50)
    
    # Load data
    manga_list, category_map, data = load_manga_data()
    if manga_list is None:
        return
    
    # Load emoji map
    emoji_map = load_emoji_map()
    
    while True:
        print("\n\033[1mSearch Options:\033[0m")
        print("1. Search for manga")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1/2): ").strip()
        
        if choice == "2":
            print("👋 Goodbye!")
            break
        
        if choice != "1":
            print("❌ Invalid choice! Please enter 1 or 2.")
            continue
        
        # Get search term from user
        search_term = input("\n🔎 Enter manga name (or part of name): ").strip()
        
        if not search_term:
            print("❌ Please enter a search term.")
            continue
        
        # Search for manga
        results = search_manga(manga_list, search_term)
        
        # Display results
        display_results(results, emoji_map)
        
        # Show additional options after search
        if results:
            print("\n\033[1mOptions:\033[0m")
            print("1. Search again")
            print("2. View details of a manga")
            print("3. Exit")
            
            sub_choice = input("\nEnter your choice (1-3): ").strip()
            
            if sub_choice == "2":
                try:
                    manga_num = int(input("Enter manga number to view details: "))
                    if 1 <= manga_num <= len(results):
                        manga = results[manga_num - 1]
                        print(f"\n📖 Detailed info for: \033[94m{manga['title']}\033[0m")
                        print(f"📚 Total categories: {len(manga['categories'])}")
                        for cat in manga['categories']:
                            emoji = emoji_map.get(cat, "•")
                            print(f"   {emoji} \033[92m{cat}\033[0m")
                        
                        # Show additional info if available
                        raw = manga['raw_data']
                        if 'chapters' in raw:
                            total_chapters = len(raw['chapters'])
                            read_chapters = sum(1 for c in raw['chapters'] if c.get('read', False))
                            print(f"📊 Chapters: {read_chapters}/{total_chapters} read")
                    else:
                        print("❌ Invalid manga number!")
                except ValueError:
                    print("❌ Please enter a valid number!")
            
            elif sub_choice == "3":
                print("👋 Goodbye!")
                break

def show_statistics(manga_list):
    """Show some statistics about the manga library"""
    total_manga = len(manga_list)
    category_count = defaultdict(int)
    
    for manga in manga_list:
        for cat in manga["categories"]:
            category_count[cat] += 1
    
    print(f"\n📊 Library Statistics:")
    print(f"Total manga: {total_manga}")
    print(f"Total categories: {len(category_count)}")
    
    # Show top 10 categories
    sorted_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n🏆 Top 10 categories by manga count:")
    for cat, count in sorted_categories:
        print(f"   {cat}: {count} manga")

if __name__ == "__main__":
    # Load data first to show statistics
    manga_list, category_map, data = load_manga_data()
    if manga_list is not None:
        show_statistics(manga_list)
        main()
    else:
        print("❌ Could not load manga data. Please make sure output/output.json exists.")