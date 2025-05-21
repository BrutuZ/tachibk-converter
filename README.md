# TACHIBK ↔ JSON Converter

### Requirements

#### Without Nix

- [Python](https://python.org) 3.7+ and depencencies:
  - `pip install -r requirements.txt`
- [ProtoC](https://github.com/protocolbuffers/protobuf/releases/latest)

#### With Nix

Using Nix, simply run `nix develop`, the shell will be created with all the depencencies.

##

### Usage

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
  --dump-schemas        Dump protobuf schemas from all supported forks
  --convert-preferences
                        Convert preference values into human-readable format.
                        [EXPERIMENTAL!] May not be encoded back into a backup file
```

#

#

Inspired by: <https://github.com/clementd64/tachiyomi-backup-models>
