#!/usr/local/bin/python

# This script will receive a JSON file, the keys are kebab-cased strings that
# will be used to generate other cases. Those generated cases will be replaced
# in the derived repository, and the value pairs are the new values that the
# replaced strings will have.
#
# Example of using this script:
# python repo-setup.py test.json

import os
import sys
import json
import shutil
import humps
from pathlib import Path

IGNORE_FOLDERS = [
    ".git",
    ".setup",
]

IGNORE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".svg",
    ".bmp",
]

ROOT = Path(os.getcwd()).parent

def main():
    os.chdir(ROOT)
    for dirpath, _, files in os.walk(ROOT):
        if is_ignored_folder(dirpath):
            continue
        for file in files:
            if is_ignored_extension(file):
                continue
            replace_file_content(os.path.join(dirpath, file))
            rename_file(file, dirpath)
    rename_folders(ROOT)
    delete_files()


def is_ignored_folder(folder: str) -> bool:
    for ignored in IGNORE_FOLDERS:
        ignored_path = f"{os.path.normpath(ROOT)}/{os.path.normpath(ignored)}/"
        real_path  = f"{os.path.normpath(folder)}/"
        if ignored_path in real_path:
            return True
    return False


def is_ignored_extension(file_name: str):
    for ignored in IGNORE_EXTENSIONS:
        if file_name.endswith(ignored):
            return True
    return False


def replace_file_content(file_path: str):
    with open(file_path,'r',errors='surrogateescape') as file:
        content = file.read()
        if not is_any_item_in_string(items=replace_dict.keys(), string=content):
            return

    with open(file_path, 'w') as file:
        print(f"REPLACE(file-content) in {file_path}")
        content = replace(content)
        file.write(content)


def rename_file(filename: str, base_path: str):
    if not is_any_item_in_string(items=replace_dict.keys(), string=filename):
        return
    new_filename = replace(filename)
    old_path = os.path.join(base_path, filename)
    new_path = os.path.join(base_path, new_filename)

    print(f"RENAME(file): {old_path} -> {new_path}")
    os.rename(old_path, new_path)


def rename_folders():
    for dirpath, _, _ in os.walk(ROOT):
        if is_ignored_folder(dirpath):
            continue
        if not is_any_item_in_string(items=replace_dict.keys(), string=dirpath):
            continue
        new_dir = replace(dirpath)
        print(f"RENAME(folder): {dirpath} -> {new_dir}")
        os.rename(dirpath, new_dir)


def is_any_item_in_string(items, string) -> bool:
    for item in items:
        if item in string:
            return True
    return False


def replace(content: str) -> str:
    for old_string in replace_dict.keys():
        if old_string in content:
            new_string = replace_dict[old_string]
            content = content.replace(old_string, new_string)
    return content


def delete_files():
    print("Deleting .github/workflows/repo-setup.yml file and .setup/ folder")
    os.remove(f"{ROOT}/.github/workflows/repo-setup.yml")
    shutil.rmtree(f"{ROOT}/.setup/")


def generate_cases(base_dict: dict) -> dict:
    # kebab-case
    new_dict = base_dict.copy()

    for key in base_dict.keys():
        # PascalCase
        new_case = humps.pascalize(base_dict[key])
        new_key = humps.pascalize(key)
        new_dict[new_key] = new_case

        # snake_case
        new_case = humps.depascalize(new_case)
        new_key = humps.depascalize(new_key)
        new_dict[new_key] = new_case

        # camelCase
        new_case = humps.camelize(base_dict[key])
        new_key = humps.camelize(key)
        new_dict[new_key] = new_case
    return new_dict


print("Script started! Loading bash input...")

values_file = open(sys.argv[1], "r")
replace_dict = generate_cases(json.loads(values_file.read()))
main()
values_file.close()

print("Script ended successfully!")
