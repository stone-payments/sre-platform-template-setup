#!/usr/local/bin/python

# This script will receive a JSON file, the keys are kebab-cased strings that
# will be used to generate other cases. Those generated cases will be replaced
# in the derived repository, and the value pairs are the new values that the
# replaced strings will have.
#
# Example of using this script:
# python repo-setup.py test.json

"""
This script helps to setup pattern in desired scaffolder repository
"""

import os
import sys
import json
import shutil
import humps

ROOT = os.environ["GITHUB_WORKSPACE"]

IGNORE_FOLDERS = [
    ".git",
    ".github",
    ".setup",
]

IGNORE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".svg",
    ".bmp",
]

DELETE_FILES = [
    ".github/workflows/repo-setup.yml"
]

DELETE_FOLDERS = [
    ".setup"
]


def is_any_item_in_string(items: list, string: str) -> bool:
    """
    is_any_item_in_string method verifies if exists desired item in content string
    """

    for item in items:
        if item in string:
            return True
    return False


def generate_cases(base_dict: dict) -> dict:
    """
    generate_cases method get dict in kebab-case and adds existing keys-values in
    differents cases
    """

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


def ignore_folder_match(ignore_folders: list, folder: str) -> bool:
    """
    folder_match method ignores folder that match pathdir in ignore folders list
    """

    for ignored in ignore_folders:
        chall_path = f"{os.path.normpath(ROOT)}/{os.path.normpath(ignored)}/"
        real_path  = f"{os.path.normpath(folder)}/"
        if chall_path in real_path:
            return True
    return False


def ignore_file_extension_match(ignore_extensions: list, file_name: str) -> bool:
    """
    file_extension_match ignores files that match filename extension in ignore extensions list
    """

    for ignored in ignore_extensions:
        if file_name.endswith(ignored):
            return True
    return False


def replace(mapped_dict: dict, content: str) -> str:
    """
    replace method has the core function to replace any content string
    """

    for old_string in mapped_dict.keys():
        if old_string in content:
            new_string = mapped_dict[old_string]
            content = content.replace(old_string, new_string)
    return content


def replace_file_content(mapped_dict: dict, file_path: str):
    """
    file_content method replace file contents to desired string value
    """

    with open(file_path,'r',errors='surrogateescape', encoding="utf-8") as file:
        content = file.read()
        if not is_any_item_in_string(items=mapped_dict.keys(), string=content):
            return

    with open(file_path, 'w', encoding="utf-8") as file:
        print(f"REPLACE(file-content) in {file_path}")
        content = replace(mapped_dict, content)
        file.write(content)


def replace_file_name(mapped_dict: dict, filename: str, base_path: str):
    """
    file_name method rename filenames to desired new name
    """

    if not is_any_item_in_string(items=mapped_dict.keys(), string=filename):
        return

    new_filename = replace(mapped_dict, filename)
    old_path = os.path.join(base_path, filename)
    new_path = os.path.join(base_path, new_filename)

    print(f"RENAME(file): {old_path} -> {new_path}")
    os.rename(old_path, new_path)


def replace_folder_name(mapped_dict: dict, root: str, ignore_folders: str):
    """
    folder_name method rename folder names to desired new name
    """

    for dirpath, _, _ in os.walk(root):
        if ignore_folder_match(ignore_folders, dirpath):
            continue
        if not is_any_item_in_string(items=mapped_dict.keys(), string=dirpath):
            continue
        new_dir = replace(mapped_dict, dirpath)
        print(f"RENAME(folder): {dirpath} -> {new_dir}")
        shutil.move(dirpath, new_dir)


def delete_files(pathfiles: list):
    """
    files method delete all files in delete files list
    """

    for pathfile in pathfiles:
        print(f"Deleting \"{pathfile}\" file")
        os.remove(f"{ROOT}/{pathfile}")


def delete_folders(pathdirs: list):
    """
    folders method delete all folders in delete folder list
    """

    for pathdir in pathdirs:
        print(f"Deleting \"{pathdir}\" folder")
        shutil.rmtree(f"{ROOT}/{pathdir}")


def main():
    """
    main code execution
    """

    os.chdir(ROOT)

    for dirpath, _, files in os.walk(ROOT):
        if ignore_folder_match(IGNORE_FOLDERS, dirpath):
            continue
        for file in files:
            if ignore_file_extension_match(IGNORE_EXTENSIONS, file):
                continue
            replace_file_content(replace_dict, os.path.join(dirpath, file))
            replace_file_name(replace_dict, file, dirpath)
    replace_folder_name(replace_dict, ROOT, IGNORE_FOLDERS)
    delete_files(DELETE_FILES)
    delete_folders(DELETE_FOLDERS)


if __name__ == "__main__":
    print("Script started! Loading bash input...")

    with open(sys.argv[1], "r", encoding="utf-8") as json_dict:
        replace_dict = generate_cases(json.loads(json_dict.read()))
        json_dict.close()

    main()

    print("Script ended successfully!")
