#!/usr/local/bin/python

# This automation file will only exist in the template repository.
# It will be removed as soon as a repository derived from this template
# is created.
#
# This script will receive a JSON file, the keys are kebab-cased strings that
# will be used to generate other cases. Those generated cases will be replaced
# in the derived repository, and the value pairs are the new values that the
# replaced strings will have.
#
# Example of using this script:
# python repo-setup.py test.json
#
# Obs.: To run this script locally, make sure that you add the item
# "build/" to the IGNORE_FOLDERS list

import os
import sys
import json
import shutil
import humps
from pathlib import Path

IGNORE_FOLDERS = [
    ".git",
    ".github",
    ".setup",
]


def main():
    root = Path(os.getcwd()).parent
    os.chdir(root)
    for dirpath, _, files in os.walk(root):
        if is_ignored_folder(dirpath):
            continue
        for file in files:
            replace_file_content(os.path.join(dirpath, file))
            rename_file(file, dirpath)
    rename_folders(root)
    delete_files()


def is_ignored_folder(folder: str) -> bool:
    for ignored in IGNORE_FOLDERS:
        if ignored in folder:
            return True
    return False


def replace_file_content(file_path: str):
    with open(file_path) as file:
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


def rename_folders(root: str):
    for dirpath, _, _ in os.walk(root):
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
    print("Deleting .github/  and .setup/ folders")
    shutil.rmtree(".github/")
    shutil.rmtree(".setup/")


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
print("===========================")
directories = os.system("ls -lha")
print(directories)
print(os.system("pwd"))
print("===========================")
values_file = open(sys.argv[1], "r")
replace_dict = generate_cases(json.loads(values_file.read()))
main()
values_file.close()

print("Script ended successfully!")
