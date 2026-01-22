![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

# 📦 Tachibk Converter

A Termux-friendly tool to convert `.tachibk`, `.proto`, and `.proto.gz` backup files (from **Tachiyomi**, **Mihon**, and forks) into readable `.json` and `.txt` formats — and restore them back to valid `.tachibk` format.

---

## ⚙️ Features

- ✅ Convert `.tachibk`, `.proto`, or `.proto.gz` → `output/output.json`
- ✅ Interactive file selector based on saved backup time
- ✅ Export categorized manga to `.txt` in `manga/sub/`
- ✅ Export source-wise manga lists in `manga/extension/`
- ✅ Filter categories from JSON using CLI interface
- ✅ Convert filtered or custom JSON back into `.tachibk`
- ✅ Re-encode `output/output.json` → `.tachibk` safely
- ✅ Supports Mihon, TachiyomiSY, J2K, Komikku, and others
- ✅ Works entirely offline after setup

---

## 🧠 Setup

### 1. Place your backup files in:

```bash
~/tachibk-converter/backup/
```

Supported formats:

- `.tachibk`
- `.proto`
- `.proto.gz`

Example:

```
backup/xyz.jmir.tachiyomi.mi_2025-06-06_11-09.tachibk
backup/tachiyomi_2023-10-02_00-51.proto.gz
```

---

### 2. Add this function to your `~/.bashrc`

```bash
tachibk() {
    files=(/storage/emulated/0/Download/Aniyomi/autobackup/*.{tachibk,proto,proto.gz})
    count=0
    for f in "${files[@]}"; do
        [ -e "$f" ] && mv "$f" ~/tachibk-converter/backup/ && ((count++))
    done
    echo -e "\e[1;33m$count file(s) moved.\e[0m"

    cd ~/tachibk-converter/ || return 1
    mkdir -p backup output explain

    CLEAN_EXPLAIN_ONLY=0

    if [[ "$1" == "--normal" ]]; then
        echo "🧠 Running explain mode..."
        bash extract_normal.sh

        latest_cleaned=$(ls -t output/output_cleaned_*.tachibk 2>/dev/null | head -n 1)
        if [ -f "$latest_cleaned" ]; then
            mv "$latest_cleaned" explain/Normal/
            echo "✅ Moved $(basename "$latest_cleaned") to explain/Normal/"
        else
            echo "❌ No cleaned .tachibk file found to move."
        fi

        CLEAN_EXPLAIN_ONLY=1
        goto_cleanup
        return
    fi
    
    if [[ "$1" == "--R18" ]]; then
        echo "🔞 Running explain mode..."
        bash extract_R18.sh

        latest_cleaned=$(ls -t output/output_cleaned_*.tachibk 2/dev/null | head -n 1)
        if [ -f "$latest_cleaned" ]; then
            mv "$latest_cleaned" explain/R18/
            echo "✅ Moved $(basename "$latest_cleaned") to explain/R18/"
        else
            echo "❌ No cleaned .tachibk file found to move."
        fi

        CLEAN_EXPLAIN_ONLY=1
        goto_cleanup
        return
    fi

    if [[ "$1" == "-h" ]]; then
        echo "📖 Tachibk Helper Tool"
        echo "========================"
        echo ""
        echo "This tool helps manage Tachiyomi backup files (.tachibk, .proto, .proto.gz)"
        echo ""
        echo "Automated steps performed:"
        echo "1. 📁 Moves backup files from /storage/emulated/0/Download/Aniyomi/autobackup/"
        echo "   to ~/tachibk-converter/backup/"
        echo "2. 🔍 Scans and displays available backup files sorted by modification time"
        echo "3. 📦 Converts selected backup to JSON format"
        echo "4. 📂 Processes the JSON to extract titles, categories, and extensions"
        echo "5. 📊 Counts and displays statistics about manga library"
        echo "6. 🧹 Cleans up generated files after processing"
        echo ""
        echo "Usage:"
        echo "  tachibk              - Normal backup processing"
        echo "  tachibk --explain    - Process normal (SFW) explain categories"
        echo "  tachibk --explain2   - Process adult (NSFW) explain categories"
        echo "  tachibk -h           - Show this help message"
        echo ""
        echo "Files created:"
        echo "  • output/output.json          - Full backup in JSON format"
        echo "  • manga/all.json              - Processed manga data with categories"
        echo "  • manga/sub/*.txt             - Category-based manga lists"
        echo "  • manga/extension/*.txt       - Extension-based manga lists"
        echo "  • output/output_cleaned_*.tachibk - Cleaned backup files (after category operations)"
        echo ""
        return 0
    fi

    echo "🔍 Scanning backup/ for backup files..."

    mapfile -t files < <(find backup/ -type f \( -name "*.tachibk" -o -name "*.proto" -o -name "*.proto.gz" \) -printf "%T@ %p\n" | sort -nr | cut -d' ' -f2-)

    if [ ${#files[@]} -eq 0 ]; then
        echo "❌ No backup files found in backup/"
        cd ~
        return 1
    fi

    echo "📦 Found backup files (newest first):"

    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    CYAN='\033[0;36m'
    RESET='\033[0m'

    now=$(date +%s)
    i=1
    for f in "${files[@]}"; do
        filename=$(basename "$f")
        mod_time=$(stat -c %Y "$f")
        diff=$((now - mod_time))

        if [ "$diff" -lt 60 ]; then
            ago="$diff sec ago"; icon="🟢"; color=$GREEN
        elif [ "$diff" -lt 3600 ]; then
            mins=$((diff / 60)); ago="$mins min ago"; icon="🟢"; color=$GREEN
        elif [ "$diff" -lt 86400 ]; then
            hours=$((diff / 3600)); mins=$(((diff % 3600) / 60))
            ago="${hours}h ${mins}m ago"; icon="🟡"; color=$YELLOW
        else
            days=$((diff / 86400)); ago="${days} day(s) ago"; icon="🔴"; color=$RED
        fi

        printf "  %2s) %b%-35s%b [%s %b%-15s%b]\n" \
            "$i" \
            "$CYAN" "$filename" "$RESET" \
            "$icon" "$color" "$ago" "$RESET"
        ((i++))
    done

    if [ ${#files[@]} -eq 1 ]; then
        echo "📦 Only one file found. Auto-selecting..."
        selection=1
    else
        echo -n "➡️  Enter the number of the file to convert: "
        read -r selection
    fi

    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#files[@]} ]; then
        echo "❌ Invalid selection."
        cd ~
        return 1
    fi

    file="${files[$((selection - 1))]}"
    filename=$(basename "$file")

    echo "📦 Selected: $filename"
    python3 tachibk-converter.py --input "$file" --output output/output.json

    if [ -f output/output.json ]; then
        echo "📂 Processing output/output.json..."
        python3 extract_titles_and_folders.py
        python3 count_cleaned_output.json_.py --file manga/all.json
    else
        echo "❌ Failed to create output/output.json"
    fi

    goto_cleanup
    cd ~
}
```

Then reload your shell:

```bash
source ~/.bashrc
```

---

## 🚀 One-Command Usage

```bash
tachibk
```

This will:

- Let you pick a `.tachibk`, `.proto`, or `.proto.gz` file from `backup/`
- Convert it to `output/output.json`
- Extract and group manga into `manga/sub/` and `manga/extension/`
- Filter categories from JSON (optional)
- Show read stats
- Let you restore to `.tachibk` using the filtered JSON

---

## 🥪 Manual Usage

```bash
python3 tachibk-converter.py --input backup/your_file.tachibk --output output/output.json --fork mihon
python3 extract_titles_and_folders.py
python3 count_cleaned_output.json_.py
python3 category_filter.py
python3 json_to_tachibk.py --input output/output.json --output restored.tachibk
```

---

## 🔁 Restore JSON → `.tachibk`

```bash
python3 json_to_tachibk.py --input output/output.json --output restored.tachibk
cp restored.tachibk /sdcard/Download/
```

You can also use your own or a filtered `.json` file (from `category_filter.py`).

Then restore it in Tachiyomi or Mihon:

```
Settings → Backup & Restore → Restore
```

---

## 📁 Folder Structure

```
tachibk-converter/
├── backup/
│   └── *.tachibk / *.proto / *.proto.gz
├── output/
│   └── output.json
├── restored.tachibk
├── tachibk-converter.py
├── json_to_tachibk.py
├── extract_titles_and_folders.py
├── count_cleaned_output.json_.py
├── category_filter.py
├── manga/
│   ├── all.json
│   ├── sub/
│   │   └── [category].txt
│   └── extension/
│       └── [source].txt
```

---

## ✅ Requirements

- Python 3
- Termux or any Linux shell
- Protobuf compiler (`protoc`) if generating schema
- Python packages:

```bash
pip install protobuf requests varint
```

---

## 📚 Notes

- Works with Mihon, SY, J2K, Komikku, etc.
- Only `.tachibk`, `.proto`, `.proto.gz` are supported
- Preferences decoding is experimental
- Safe: does not modify original backups

---

## 🙏 Credits

- Based on [BrutuZ/tachibk-converter](https://github.com/BrutuZ/tachibk-converter)
- Extended and maintained by [@Mohin2295747](https://github.com/Mohin2295747) for Termux + Mihon support