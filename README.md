# TACHIBK to JSON Converter

### Requirements:

- [Python](https://python.org) 3.7+ and depencencies:
  - `pip install -r requirements.txt`
- [ProtoC](https://github.com/protocolbuffers/protobuf/releases/latest)

##

### Usage:

#### Convert backup to json

```
python tachibk-converter.py [-h] [--input <backup_file.tachibk | backup_file.proto.gz>] [--output <output.json>] [--fork <mihon | sy | j2k>]

options:
  -h, --help            show this help message and exit
  --input <backup_file.tachibk | backup_file.proto.gz>, -i <backup_file.tachibk | backup_file.proto.gz>
  --output <output.json>, -o <output.json>
  --fork <mihon | sy | j2k>
```

#### Convert json to backup
```
python tachibk-creater.py [-h] [--input <converted_file.json>] [--output <backup_file.tachibk | backup_file.proto.gz>]
[--fork <mihon | sy | j2k>]

options:
  -h, --help            show this help message and exit
  --input <converted_file.json>, -i <converted_file.json>
  --output <backup_file.tachibk | backup_file.proto.gz>, -o <backup_file.proto.gz>

#

#

Inspired by: https://github.com/clementd64/tachiyomi-backup-models
