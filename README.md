# TACHIBK ↔ JSON Converter

### Requirements:

- [Python](https://python.org) 3.7+ and depencencies:
  - `pip install -r requirements.txt`
- [ProtoC](https://github.com/protocolbuffers/protobuf/releases/latest)

##

### Usage:

```
python usage: tachibk-converter.py [-h] [--input <backup_file.tachibk | backup_file.proto.gz | decoded_backup.json>] [--output <output.json | encoded_backup.tachibk>] [--fork <mihon | sy | j2k>]

options:
  -h, --help            show this help message and exit
  --input, -i <backup_file.tachibk | backup_file.proto.gz | decoded_backup.json>
                        File extension defines whether to decode a backup file to JSON or encode it back
  --output, -o <output.json | encoded_backup.tachibk>
                        When encoding, TACHIBK or PROTO.GZ will additionally recompress the backup file
  --fork <mihon | sy | j2k>
                        Use backup schema from the following fork. Default: Mihon
```

#

#

Inspired by: https://github.com/clementd64/tachiyomi-backup-models
