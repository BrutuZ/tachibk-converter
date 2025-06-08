# TACHIBK ↔ JSON Converter

## Requirements

- [Python](https://python.org) 3.9+
- [ProtoC](https://github.com/protocolbuffers/protobuf/releases/latest)

## Installation

### Pip

1. Clone the repo `git clone https://github.com/BrutuZ/tachibk-converter.git`
2. Navigate to the created folder: `cd tachibk-converter`
3. Create a Virtual Environment: `python -m venv .`
4. Activate the venv:
    - Linux: `source bin/activate`
    - Windows: `Scripts\activate.bat`
5. Install dependencies: `pip install -r requirements.txt`
6. Run `python tachibk_converter.py`

### [UV](https://github.com/astral-sh/uv)
_There are 2 methods available:_

---
1. Clone the repo `git clone https://github.com/BrutuZ/tachibk-converter.git`
2. Navigate to the created folder: `cd tachibk-converter`
3. Run `uv run tachibk_converter [parameters]`
---
1. Run `uvx --from git+https://github.com/BrutuZ/tachibk-converter tachibk_converter [parameters]`
  
### [Nix](https://nixos.org)

1. Run `nix develop`, the shell will be created with all the depencencies

## Usage

```
tachibk_converter [-h] [--input <backup_file.tachibk | backup_file.proto.gz | decoded_backup.json>] [--output <output.json | encoded_backup.tachibk>] [--fork <mihon | sy | j2k | komikku>]

options:
  -h, --help            show this help message and exit
  --input, -i <backup_file.tachibk | backup_file.proto.gz | decoded_backup.json>
                        File extension defines whether to decode a backup file to JSON or encode it back
  --output, -o <output.json | encoded_backup.tachibk>
                        When encoding, TACHIBK or PROTO.GZ will additionally recompress the backup file
  --fork <mihon | sy | j2k | komikku>
                        Use backup schema from the following fork. Default: Mihon
  --dump-schemas        Dump protobuf schemas from all supported forks
  --convert-preferences
                        Convert preference values into human-readable format.
                        [EXPERIMENTAL!] May not be encoded back into a backup file
```

#

#

Inspired by: <https://github.com/clementd64/tachiyomi-backup-models>
