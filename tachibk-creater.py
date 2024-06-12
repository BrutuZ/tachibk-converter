import gzip
from argparse import ArgumentParser
from pathlib import Path
from google.protobuf.json_format import Parse, ParseError

argp = ArgumentParser()
argp.add_argument(
    "--input",
    "-i",
    default="output.json",
    metavar="<converted_file.json>",
    type=Path
)
argp.add_argument(
    "--output",
    "-o",
    default="backup_file.tachibk",
    metavar='<backup_file.tachibk | backup_file.proto.gz>',
    type=Path,
)

args = argp.parse_args()

try:
    from schema_pb2 import Backup
except (ModuleNotFoundError, NameError):
    print('No protobuf schema found... ABORTING!')
    print("Run tachibk-converter.py first.")

def parse_json():
    try:
        with open(args.input) as file:
            json_string = file.read()
    except OSError:
        print('ERROR! No JSON to process.')
        argp.print_help()
        exit(1)
    try:
        return Parse(json_string, Backup()).SerializeToString()
    except ParseError:
        print("The input JSON file is invalid.")
        exit(1)

def write_backup(message):
        if str(args.output).endswith('.proto.gz') or str(args.output).endswith('.tachibk'):
            with gzip.open(args.output, "wb") as zip:
                zip.write(message)
        else:
            with open(str(args.output), "wb") as file:
                file.write(message)
        print(f"Backup written to {args.output}")


if __name__ == "__main__":
    write_backup(parse_json())

