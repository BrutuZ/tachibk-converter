import json
import gzip
import varint
import os
import re
from base64 import b64encode
from struct import pack
from google.protobuf.json_format import Parse, ParseError

# ✅ Make sure schema_pb2 can be found
import sys
sys.path.insert(0, './manga/proto')
from schema_pb2 import Backup

b64_pattern = re.compile(r'^[A-Za-z0-9+/=]{4,}$')

def bytes_preference(preference_value: dict):
    true_value = preference_value['value']['truevalue']
    ptype = preference_value['value']['type'].split('.')[-1].removesuffix('PreferenceValue')

    try:
        if isinstance(true_value, str) and b64_pattern.match(true_value):
            return true_value  # Already encoded, leave as-is

        if ptype == 'Boolean':
            return b64encode(b'\x08' + (b'\x01' if true_value else b'\x00')).decode()
        elif ptype in ['Int', 'Long']:
            return b64encode(b'\x08' + varint.encode(int(true_value))).decode()
        elif ptype == 'Float':
            return b64encode(b'\r' + pack('f', float(true_value))).decode()
        elif ptype == 'String':
            encoded = true_value.encode('utf-8')
            length = len(encoded)
            return b64encode(b'\n' + length.to_bytes(2, 'little') + encoded).decode()
        elif ptype == 'StringSet':
            new_bytes = b''
            for val in true_value:
                encoded = val.encode('utf-8')
                length = len(encoded)
                new_bytes += b'\n' + length.to_bytes(2, 'little') + encoded
            return b64encode(new_bytes).decode()
        else:
            print(f"⚠️ Unknown preference type: {ptype}, skipping.")
            return ''
    except Exception as e:
        print(f"⚠️ Error encoding preference '{preference_value['key']}': {e}")
        return ''

def convert_json_to_bytes(path: str) -> bytes:
    with open(path, "r", encoding="utf-8") as f:
        message_dict = json.load(f)

    def needs_encoding(val):
        return not isinstance(val, str) or not b64_pattern.match(val)

    for pref in message_dict.get("backupPreferences", []):
        if needs_encoding(pref["value"]["truevalue"]):
            pref["value"]["truevalue"] = bytes_preference(pref)

    for source in message_dict.get("backupSourcePreferences", []):
        for pref in source.get("prefs", []):
            if needs_encoding(pref["value"]["truevalue"]):
                pref["value"]["truevalue"] = bytes_preference(pref)

    try:
        return Parse(json.dumps(message_dict), Backup()).SerializeToString()
    except ParseError as e:
        print("❌ Invalid JSON backup:", e)
        exit(1)

def write_tachibk(message_bytes: bytes, output_path: str):
    with gzip.open(output_path, "wb") as f:
        f.write(message_bytes)
    print(f"✅ Compressed backup written to {output_path}")

def list_json_files_sorted(directory="output"):
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
    return files

def main():
    print("\n\033[1mAvailable JSON files (newest first):\033[0m")
    files = list_json_files_sorted()

    if not files:
        print("❌ No .json files found in the output/ directory.")
        return

    for i, file in enumerate(files, 1):
        timestamp = os.path.getmtime(os.path.join("output", file))
        print(f"\033[96m{i:>2}.\033[0m {file} \033[90m(last modified: {timestamp:.0f})\033[0m")

    selected = input("\nEnter the number of the JSON file to convert: ").strip()
    if not selected.isdigit() or not (1 <= int(selected) <= len(files)):
        print("❌ Invalid selection.")
        return

    selected_file = files[int(selected) - 1]
    input_path = os.path.join("output", selected_file)
    output_path = os.path.join("output", selected_file.replace(".json", ".tachibk"))

    msg = convert_json_to_bytes(input_path)
    write_tachibk(msg, output_path)

if __name__ == "__main__":
    main()