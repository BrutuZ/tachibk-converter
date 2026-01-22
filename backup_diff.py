#!/usr/bin/env python3

#compare two files
import json
import gzip
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import argparse
from datetime import datetime

sys.path.insert(0, './manga/proto')

def get_tachibk_files(directory: str = ".") -> List[Tuple[str, float, str]]:
    tachibk_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tachibk'):
                file_path = os.path.join(root, file)
                mtime = os.path.getmtime(file_path)
                tachibk_files.append((file_path, mtime, file))
    tachibk_files.sort(key=lambda x: x[1], reverse=True)
    return tachibk_files

def filter_out_diff_files(files: List[Tuple[str, float, str]]) -> List[Tuple[str, float, str]]:
    filtered = []
    for file_path, mtime, filename in files:
        if not filename.startswith('diff_'):
            filtered.append((file_path, mtime, filename))
    return filtered

def display_file_choices(files: List[Tuple[str, float, str]], title: str = "Available TACHIBK files:"):
    print(f"\n\033[1m{title}\033[0m")
    print("=" * 60)
    for i, (file_path, mtime, filename) in enumerate(files, 1):
        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        print(f"\033[94m{i:>2}.\033[0m {filename}")
        print(f"     📅 {time_str}")
        print(f"     📍 {file_path}")
    print("=" * 60)
    return files

def select_files_interactive():
    print("\n\033[1m🔍 Tachiyomi Backup Diff Tool\033[0m")
    all_files = []
    for directory in [".", "backup", "output"]:
        if os.path.exists(directory):
            all_files.extend(get_tachibk_files(directory))
    if not all_files:
        print("\n❌ No .tachibk files found")
        sys.exit(1)
    seen = set()
    unique_files = []
    for file_path, mtime, filename in all_files:
        if filename not in seen:
            seen.add(filename)
            unique_files.append((file_path, mtime, filename))
    non_diff_files = filter_out_diff_files(unique_files)
    if not non_diff_files:
        print("\n❌ No regular backup files found")
        sys.exit(1)
    files = display_file_choices(non_diff_files, "Available Backup Files:")
    while True:
        try:
            choice1 = input("\nSelect OLDER backup (first number): ").strip()
            if not choice1.isdigit():
                continue
            idx1 = int(choice1) - 1
            if 0 <= idx1 < len(files):
                file1 = files[idx1][0]
                print(f"✓ Selected: {files[idx1][2]}")
                break
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    while True:
        try:
            choice2 = input("Select NEWER backup (second number): ").strip()
            if not choice2.isdigit():
                continue
            idx2 = int(choice2) - 1
            if 0 <= idx2 < len(files):
                if idx2 == idx1:
                    print("Cannot select the same file twice")
                    continue
                file2 = files[idx2][0]
                print(f"✓ Selected: {files[idx2][2]}")
                break
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    return file1, file2

def load_tachibk_file(file_path: str) -> Dict[str, Any]:
    print(f"Loading: {os.path.basename(file_path)}...")
    try:
        with gzip.open(file_path, 'rb') as f:
            backup_data = f.read()
        from schema_pb2 import Backup
        from google.protobuf.json_format import MessageToDict
        message = Backup()
        message.ParseFromString(backup_data)
        data = MessageToDict(message)
        return data
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        sys.exit(1)

def compare_backups_simple(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    changes = {
        'backupManga': [],
        'backupCategories': [],
        'backupSources': [],
        'backupPreferences': [],
        'backupSourcePreferences': [],
        'backupExtensionRepo': [],
    }
    print("\n🔍 Analyzing changes...")
    
    old_manga_dict = {}
    for manga in old_data.get('backupManga', []):
        source = manga.get('source', 'unknown')
        url = manga.get('url', 'unknown')
        key = f"{source}::{url}"
        old_manga_dict[key] = manga
    
    new_manga_dict = {}
    for manga in new_data.get('backupManga', []):
        source = manga.get('source', 'unknown')
        url = manga.get('url', 'unknown')
        key = f"{source}::{url}"
        new_manga_dict[key] = manga
    
    old_keys = set(old_manga_dict.keys())
    new_keys = set(new_manga_dict.keys())
    
    added = new_keys - old_keys
    removed = old_keys - new_keys
    common = old_keys & new_keys
    
    print(f"  Manga: {len(added)} added, {len(removed)} removed, {len(common)} common")
    
    all_used_categories = set()
    all_used_sources = set()
    manga_count = 0
    
    for key in new_keys:
        if key in added:
            changes['backupManga'].append(new_manga_dict[key])
            manga_count += 1
            manga_data = new_manga_dict[key]
            if 'categories' in manga_data:
                all_used_categories.update(manga_data['categories'])
            if 'source' in manga_data:
                all_used_sources.add(str(manga_data['source']))
        elif key in common:
            old_manga = old_manga_dict[key]
            new_manga = new_manga_dict[key]
            old_str = json.dumps(old_manga, sort_keys=True)
            new_str = json.dumps(new_manga, sort_keys=True)
            if old_str != new_str:
                changes['backupManga'].append(new_manga)
                manga_count += 1
                if 'categories' in new_manga:
                    all_used_categories.update(new_manga['categories'])
                if 'source' in new_manga:
                    all_used_sources.add(str(new_manga['source']))
    
    print(f"  Total manga in diff: {manga_count}")
    print(f"  Categories used by changed manga: {len(all_used_categories)}")
    print(f"  Sources used by changed manga: {len(all_used_sources)}")
    
    new_categories_dict = {cat.get('order'): cat for cat in new_data.get('backupCategories', [])}
    for cat_id in all_used_categories:
        cat_id_str = str(cat_id)
        for cat_order, cat_data in new_categories_dict.items():
            if str(cat_order) == cat_id_str:
                if cat_data not in changes['backupCategories']:
                    changes['backupCategories'].append(cat_data)
                break
    
    changes['backupPreferences'] = new_data.get('backupPreferences', [])
    changes['backupSourcePreferences'] = new_data.get('backupSourcePreferences', [])
    changes['backupExtensionRepo'] = new_data.get('backupExtensionRepo', [])
    
    print(f"  Preferences: ALL included ({len(changes['backupPreferences'])} total)")
    print(f"  Source Preferences: ALL included ({len(changes['backupSourcePreferences'])} total)")
    
    new_sources_dict = {src.get('id'): src for src in new_data.get('backupSources', [])}
    for source_id in all_used_sources:
        for src_id, src_data in new_sources_dict.items():
            if str(src_id) == source_id:
                if src_data not in changes['backupSources']:
                    changes['backupSources'].append(src_data)
                break
    
    return changes

def print_simple_summary(changes: Dict[str, Any], old_filename: str, new_filename: str, old_count: int, new_count: int):
    print("\n" + "="*70)
    print("📊 BACKUP DIFF SUMMARY")
    print("="*70)
    print(f"\n📁 Files:")
    print(f"   Old: {os.path.basename(old_filename)} ({old_count} manga)")
    print(f"   New: {os.path.basename(new_filename)} ({new_count} manga)")
    manga_count = len(changes.get('backupManga', []))
    cat_count = len(changes.get('backupCategories', []))
    pref_count = len(changes.get('backupPreferences', []))
    print(f"\n📚 Changes to be included in diff backup:")
    print(f"   📦 Manga: {manga_count}")
    print(f"   📁 Categories: {cat_count}")
    print(f"   ⚙️ Preferences: ALL ({pref_count} total)")
    if new_count > 0:
        percentage = (manga_count / new_count) * 100
        print(f"   📊 Manga coverage: {percentage:.1f}% of new backup")
    manga_list = changes.get('backupManga', [])
    if manga_list:
        print(f"\n📖 Example manga in diff (first 5):")
        for i, manga in enumerate(manga_list[:5]):
            title = manga.get('title', 'Unknown')
            if len(title) > 50:
                title = title[:47] + "..."
            print(f"   {i+1:>2}. {title}")
    print("\n" + "="*70)

def save_changes_as_tachibk(changes: Dict[str, Any], output_path: str):
    try:
        print(f"\n🔄 Creating TACHIBK file...")
        total_items = sum(len(v) for v in changes.values() if isinstance(v, list))
        if total_items == 0:
            print("❌ No changes to save! Diff would be empty.")
            return False
        temp_json = output_path.replace('.tachibk', '_temp.json')
        with open(temp_json, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Created temporary JSON: {temp_json}")
        try:
            from json_to_tachibk import convert_json_to_bytes
            print("  ✓ Converting JSON to TACHIBK...")
            message_bytes = convert_json_to_bytes(temp_json)
            with gzip.open(output_path, 'wb') as f:
                f.write(message_bytes)
            file_size = os.path.getsize(output_path)
            print(f"\n✅ Diff backup saved to: {output_path}")
            print(f"   File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            if os.path.exists(temp_json):
                os.remove(temp_json)
            return True
        except ImportError:
            import subprocess
            result = subprocess.run(
                ['python', 'tachibk-converter.py', '--input', temp_json, '--output', output_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"\n✅ Diff backup saved to: {output_path}")
                if os.path.exists(temp_json):
                    os.remove(temp_json)
                return True
            else:
                print(f"❌ Conversion failed: {result.stderr}")
                return False
    except Exception as e:
        print(f"❌ Error creating TACHIBK: {type(e).__name__}: {e}")
        return False

def generate_output_filename(old_file: str, new_file: str) -> str:
    old_name = os.path.basename(old_file).replace('.tachibk', '')
    new_name = os.path.basename(new_file).replace('.tachibk', '')
    old_date = "old"
    new_date = "new"
    import re
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    old_match = re.search(date_pattern, old_name)
    new_match = re.search(date_pattern, new_name)
    if old_match:
        old_date = old_match.group(1)
    if new_match:
        new_date = new_match.group(1)
    os.makedirs("output", exist_ok=True)
    return f"output/diff_{old_date}_to_{new_date}.tachibk"

def main():
    parser = argparse.ArgumentParser(description='Compare two Tachiyomi .tachibk files and create a diff backup')
    parser.add_argument('files', nargs='*', help='Optional: Specify two .tachibk files to compare')
    args = parser.parse_args()
    
    if len(args.files) == 2:
        file1, file2 = args.files
        file1_name = os.path.basename(file1)
        file2_name = os.path.basename(file2)
        if file1_name.startswith('diff_'):
            response = input(f"❌ Warning: {file1_name} is a diff file. Continue? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(0)
        if file2_name.startswith('diff_'):
            response = input(f"❌ Warning: {file2_name} is a diff file. Continue? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(0)
        print(f"\n\033[1m🔍 Comparing:\033[0m")
        print(f"   Old: {file1_name}")
        print(f"   New: {file2_name}")
        if not os.path.exists(file1):
            print(f"❌ File not found: {file1}")
            sys.exit(1)
        if not os.path.exists(file2):
            print(f"❌ File not found: {file2}")
            sys.exit(1)
    elif len(args.files) == 0:
        file1, file2 = select_files_interactive()
    else:
        print("❌ Please specify exactly 2 .tachibk files")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("📖 LOADING BACKUPS")
    print("="*60)
    
    old_data = load_tachibk_file(file1)
    new_data = load_tachibk_file(file2)
    
    old_count = len(old_data.get('backupManga', []))
    new_count = len(new_data.get('backupManga', []))
    
    print(f"✅ Backups loaded")
    print(f"   Old: {old_count} manga")
    print(f"   New: {new_count} manga")
    
    changes = compare_backups_simple(old_data, new_data)
    print_simple_summary(changes, file1, file2, old_count, new_count)
    
    manga_changes = len(changes.get('backupManga', []))
    if manga_changes == 0:
        print("\n⚠️  WARNING: No manga changes!")
        response = input("Create empty diff? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    else:
        response = input("\nCreate diff backup? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    output_file = generate_output_filename(file1, file2)
    print(f"\n🛠️ Creating diff backup...")
    success = save_changes_as_tachibk(changes, output_file)
    
    if success:
        print("\n🎉 Diff complete!")
        print(f"\n📁 Contains:")
        print(f"   • {manga_changes} manga")
        print(f"   • {len(changes.get('backupCategories', []))} categories")
        print(f"   • ALL preferences ({len(changes.get('backupPreferences', []))} total)")
        print(f"\n💾 File: {os.path.abspath(output_file)}")
        if manga_changes > 0:
            print(f"\n📝 Restore on '{os.path.basename(file1)}' to update to '{os.path.basename(file2)}'.")
    else:
        print("\n❌ Failed")

if __name__ == '__main__':
    main()