#!/bin/bash

# CONFIG - Exact category names you want to keep
SELECTED_CATEGORIES=(
    "🤔name of category"
)

BACKUP_DIR="backup"
OUTPUT_DIR="output"

echo "🔍 Scanning $BACKUP_DIR/ for backup files..."
mapfile -t BACKUP_FILES < <(find "$BACKUP_DIR" -type f \( -name "*.tachibk" -o -name "*.proto.gz" \) -printf "%T@ %p\n" | sort -nr | cut -d' ' -f2-)

if [ ${#BACKUP_FILES[@]} -eq 0 ]; then
    echo "❌ No .tachibk or .proto.gz files found in $BACKUP_DIR/"
    exit 1
fi

echo "📦 Found backup files (sorted by time):"

# Color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RESET='\033[0m'

now=$(date +%s)

for i in "${!BACKUP_FILES[@]}"; do
    file="${BACKUP_FILES[$i]}"
    filename="${file##*/}"
    
    mod_time=$(stat -c %Y "$file")
    diff=$((now - mod_time))

    if [ "$diff" -lt 60 ]; then
        ago="$diff sec ago"
    elif [ "$diff" -lt 3600 ]; then
        mins=$((diff / 60))
        ago="$mins min ago"
    elif [ "$diff" -lt 86400 ]; then
        hours=$((diff / 3600))
        mins=$(((diff % 3600) / 60))
        ago="${hours}h ${mins}m ago"
    else
        days=$((diff / 86400))
        ago="${days} day(s) ago"
    fi

    printf "  %s) %b%s%b  [%b%s%b]\n" \
        "$((i+1))" \
        "$CYAN" "$filename" "$RESET" \
        "$GREEN" "$ago" "$RESET"
done

read -p "➡️  Enter the number of the file to convert: " file_num
SELECTED_FILE="${BACKUP_FILES[$((file_num-1))]}"
echo "📦 Selected: ${SELECTED_FILE##*/}"

# Decode the backup
python3 tachibk-converter.py --input "$SELECTED_FILE" --output "$OUTPUT_DIR/output.json"

if [ ! -f "$OUTPUT_DIR/output.json" ]; then
    echo "❌ output.json not found after decoding!"
    exit 1
fi

echo "📂 Filtering categories..."

# Get current counter based on existing output_cleaned_direct_N.json files
max_index=0
for ((i=1; i<=5; i++)); do
    if [ -f "$OUTPUT_DIR/output_cleaned_direct_${i}.json" ]; then
        max_index=$i
    fi
done

# Next index (wrap around after 5)
next_index=$((max_index + 1))
if [ "$next_index" -gt 5 ]; then
    next_index=1
fi

CLEANED_JSON="$OUTPUT_DIR/output_cleaned_direct_${next_index}.json"

# Create a temporary Python script
TMP_SCRIPT=$(mktemp)
cat << 'EOF' > "$TMP_SCRIPT"
import json
import sys
from collections import defaultdict

def main():
    target_categories = sys.argv[1:-1]
    output_file = sys.argv[-1]

    with open("output/output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    category_map = {}
    for cat in data.get("backupCategories", []):
        order = cat.get("order", -1)
        name = cat.get("name", "").strip()
        if order != -1 and name:
            category_map[str(order)] = name

    filtered_manga = []
    selected_categories = set()

    for manga in data.get("backupManga", []):
        keep = False
        categories = manga.get("categories", [])

        for cat_id in categories:
            cat_name = category_map.get(str(cat_id), "")
            if cat_name in target_categories:
                keep = True
                selected_categories.add(cat_name)

        if not categories and "Uncategorized" in target_categories:
            keep = True
            selected_categories.add("Uncategorized")

        if keep:
            new_categories = [
                cat_id for cat_id in categories
                if category_map.get(str(cat_id), "") in target_categories
            ]
            manga["categories"] = new_categories
            filtered_manga.append(manga)

    if not selected_categories:
        print("❌ None of the target categories were found in any manga!", file=sys.stderr)
        return 1

    used_cat_ids = set()
    for manga in filtered_manga:
        used_cat_ids.update(manga.get("categories", []))

    data["backupManga"] = filtered_manga
    data["backupCategories"] = [
        cat for cat in data.get("backupCategories", [])
        if cat.get("order") in used_cat_ids
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned data saved to {output_file}")
    print(f"Selected categories: {', '.join(sorted(selected_categories))}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

# Run the filter script
python3 "$TMP_SCRIPT" "${SELECTED_CATEGORIES[@]}" "$CLEANED_JSON"
rm -f "$TMP_SCRIPT"

if [ $? -ne 0 ]; then
    exit 1
fi

echo "✅ Using cleaned JSON: $CLEANED_JSON"

# Re-encode to tachibk
if ! python3 json_to_tachibk.py --input "$CLEANED_JSON" --output "$OUTPUT_DIR/$(basename "${CLEANED_JSON%.json}.tachibk")"; then
    echo "❌ Failed to re-encode JSON to .tachibk"
    exit 1
fi

echo "🎉 Done! Final .tachibk saved in $OUTPUT_DIR/"