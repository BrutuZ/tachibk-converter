# TACHIBK to JSON Converter

### Requirements:

- [Python](https://python.org) 3.7+ and depencencies:
  - `pip install -r requirements.txt`
- [ProtoC](https://github.com/protocolbuffers/protobuf/releases/latest)

##

### Usage:

```
python tachibk-converter.py [-h] [--input <backup_file.tachibk | backup_file.proto.gz>] [--output <output.json>] [--fork <mihon | sy | j2k>]

options:
  -h, --help            show this help message and exit
  --input <backup_file.tachibk | backup_file.proto.gz>, -i <backup_file.tachibk | backup_file.proto.gz>
  --output <output.json>, -o <output.json>
  --fork <mihon | sy | j2k>
```

#

#

Inspired by: https://github.com/clementd64/tachiyomi-backup-models
