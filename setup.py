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

class Tool:
    def is_any_item_in_string(items: list, string: str) -> bool:
        for item in items:
            if item in string:
                return True
        return False

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

class Ignore:
    def __init__(self, folders, extensions) -> None:
        self.folders   = folders
        self.extensions = extensions

    def folder_match(self, folder: str) -> bool:
        for ignored in self.folders:
            chall_path = f"{os.path.normpath(ROOT)}/{os.path.normpath(ignored)}/"
            real_path  = f"{os.path.normpath(folder)}/"
            if chall_path in real_path:
                return True
        return False

    def file_extension_match(self, file_name: str) -> bool:
        for ignored in self.extensions:
            if file_name.endswith(ignored):
                return True
        return False

class Replace:
    def __init__(self, replace_dict: dict, ignore: Ignore) -> None:
        self.replace_dict   = replace_dict
        self.ignore = ignore
        
    def replace(self, content: str) -> str:
        for old_string in self.replace_dict.keys():
            if old_string in content:
                new_string = self.replace_dict[old_string]
                content = content.replace(old_string, new_string)
        return content

    def file_content(self, file_path: str):
        with open(file_path,'r',errors='surrogateescape') as file:
            content = file.read()
            if not Tool.is_any_item_in_string(items=self.replace_dict.keys(), string=content):
                return

        with open(file_path, 'w') as file:
            print(f"REPLACE(file-content) in {file_path}")
            content = self.replace(content)
            file.write(content)

    def file_name(self, filename: str, base_path: str):
        if not Tool.is_any_item_in_string(items=self.replace_dict.keys(), string=filename):
            return
        
        new_filename = self.replace(filename)
        old_path = os.path.join(base_path, filename)
        new_path = os.path.join(base_path, new_filename)

        print(f"RENAME(file): {old_path} -> {new_path}")
        os.rename(old_path, new_path)

    def folder_name(self, root: str):
        for dirpath, _, _ in os.walk(root):
            if self.ignore.folder_match(dirpath):
                continue
            if not Tool.is_any_item_in_string(items=self.replace_dict.keys(), string=dirpath):
                continue
            new_dir = self.replace(dirpath)
            print(f"RENAME(folder): {dirpath} -> {new_dir}")
            shutil.move(dirpath, new_dir)

class Delete:
    def __init__(self, file_list, folder_list) -> None:
        self.file_list = file_list
        self.folder_list = folder_list
        
    def files(self):
        for pathfile in self.file_list:
            print(f"Deleting \"{pathfile}\" file")
            os.remove(f"{ROOT}/{pathfile}")

    def folders(self):
        for pathdir in self.folder_list:
            print(f"Deleting \"{pathdir}\" folder")
            shutil.rmtree(f"{ROOT}/{pathdir}")
            
def main():
    root = Path(os.getcwd()).parent
    os.chdir(root)
    delete  = Delete(DELETE_FILES, DELETE_FOLDERS)
    ignore  = Ignore(IGNORE_FOLDERS, IGNORE_EXTENSIONS)
    replace = Replace(replace_dict, ignore)

    for dirpath, _, files in os.walk(root):
        if ignore.folder_match(dirpath):
            continue
        for file in files:
            if ignore.file_extension_match(file):
                continue
            replace.file_content(os.path.join(dirpath, file))
            replace.file_name(file, dirpath)
    replace.folder_name(root)
    delete.files()
    delete.folders()

if __name__ == "__main__":
    print("Script started! Loading bash input...")
    values_file = open(sys.argv[1], "r")
    replace_dict = Tool.generate_cases(json.loads(values_file.read()))
    
    main()

    values_file.close()
    print("Script ended successfully!")
