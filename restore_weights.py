#!/usr/bin/env python3
"""Verify and join raw checkpoint parts using only the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_child(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path outside selected directory: {name}')
    return path


def restore(entry, parts_dir, output_dir, verify_only=False):
    destination = safe_child(output_dir, entry['output_directory'] + '/' + entry['filename'])
    if destination.exists() and not verify_only:
        if destination.stat().st_size == entry['bytes'] and digest(destination) == entry['sha256']:
            print(f'Already verified: {destination}', flush=True)
            return
        raise ValueError(f'Refusing to overwrite an existing mismatched file: {destination}')
    paths = []
    for part in entry['parts']:
        path = safe_child(parts_dir, part['name'])
        if path.stat().st_size != part['bytes']:
            raise ValueError(f'Part size mismatch: {path}')
        paths.append((part, path))
    temporary = destination.with_name(destination.name + '.reconstructing')
    stream = None
    if not verify_only:
        destination.parent.mkdir(parents=True, exist_ok=True)
        stream = temporary.open('xb')
    whole = hashlib.sha256()
    size = 0
    try:
        for part, path in paths:
            h = hashlib.sha256()
            with path.open('rb') as source:
                for chunk in iter(lambda: source.read(8 * 1024 * 1024), b''):
                    h.update(chunk)
                    whole.update(chunk)
                    size += len(chunk)
                    if stream:
                        stream.write(chunk)
            if h.hexdigest() != part['sha256']:
                raise ValueError(f'Part SHA-256 mismatch: {path}')
            print(f'Verified: {part["name"]}', flush=True)
        if size != entry['bytes'] or whole.hexdigest() != entry['sha256']:
            raise ValueError(f'Whole checkpoint integrity failure: {entry["id"]}')
        if stream:
            stream.close()
            stream = None
            # Publish only after every part and the complete checkpoint match.
            if destination.exists():
                raise FileExistsError(destination)
            temporary.rename(destination)
        print(f'{"Verified" if verify_only else "Restored"}: {entry["id"]} ({size} bytes)', flush=True)
    except BaseException:
        if stream:
            stream.close()
        if not verify_only:
            temporary.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('manifest.json'))
    parser.add_argument('--parts-dir', type=Path, default=Path('.'))
    parser.add_argument('--output-dir', type=Path, default=Path('weights'))
    parser.add_argument('--only', choices=['step200', 'step1000'])
    parser.add_argument('--verify-only', action='store_true', help='Verify all part hashes and combined bytes without writing weights')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    entries = manifest['files']
    if args.only:
        entries = [entry for entry in entries if entry['step'] == int(args.only[4:])]
    if not entries:
        parser.error('No checkpoints matched')
    for entry in entries:
        restore(entry, args.parts_dir, args.output_dir, args.verify_only)


if __name__ == '__main__':
    main()
