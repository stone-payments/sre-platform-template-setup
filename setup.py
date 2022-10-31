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

from pathlib import Path
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


class Tool:
    """
    Tool class contains helpful methods general in general
    """

    @staticmethod
    def is_any_item_in_string(items: list, string: str) -> bool:
        """
        is_any_item_in_string method verifies if exists desired item in content string
        """

        for item in items:
            if item in string:
                return True
        return False

    @staticmethod
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


class Ignore:
    """
    Ignore class is responsible to ignore folders and files
    """

    def __init__(self, folders: list, extensions: list) -> None:
        self.folders   = folders
        self.extensions = extensions

    def folder_match(self, folder: str) -> bool:
        """
        folder_match method ignores folder that match pathdir in ignore folders list
        """

        for ignored in self.folders:
            chall_path = f"{os.path.normpath(ROOT)}/{os.path.normpath(ignored)}/"
            real_path  = f"{os.path.normpath(folder)}/"
            if chall_path in real_path:
                return True
        return False

    def file_extension_match(self, file_name: str) -> bool:
        """
        file_extension_match ignores files that match filename extension in ignore extensions list
        """

        for ignored in self.extensions:
            if file_name.endswith(ignored):
                return True
        return False


class Replace:
    """
    Replace class is responsible to replace any content, files or folders in scaffolder repository.
    """

    def __init__(self, replace_dict_values: dict, ignore: Ignore) -> None:
        self.replace_dict = replace_dict_values
        self.ignore = ignore

    def replace(self, content: str) -> str:
        """
        replace method has the core function to replace any content string
        """

        for old_string in self.replace_dict.keys():
            if old_string in content:
                new_string = self.replace_dict[old_string]
                content = content.replace(old_string, new_string)
        return content

    def file_content(self, file_path: str):
        """
        file_content method replace file contents to desired string value
        """

        with open(file_path,'r',errors='surrogateescape', encoding="utf-8") as file:
            content = file.read()
            if not Tool.is_any_item_in_string(items=self.replace_dict.keys(), string=content):
                return

        with open(file_path, 'w', encoding="utf-8") as file:
            print(f"REPLACE(file-content) in {file_path}")
            content = self.replace(content)
            file.write(content)

    def file_name(self, filename: str, base_path: str):
        """
        file_name method rename filenames to desired new name
        """

        if not Tool.is_any_item_in_string(items=self.replace_dict.keys(), string=filename):
            return

        new_filename = self.replace(filename)
        old_path = os.path.join(base_path, filename)
        new_path = os.path.join(base_path, new_filename)

        print(f"RENAME(file): {old_path} -> {new_path}")
        os.rename(old_path, new_path)

    def folder_name(self, root: str):
        """
        folder_name method rename folder names to desired new name
        """

        for dirpath, _, _ in os.walk(root):
            if self.ignore.folder_match(dirpath):
                continue
            if not Tool.is_any_item_in_string(items=self.replace_dict.keys(), string=dirpath):
                continue
            new_dir = self.replace(dirpath)
            print(f"RENAME(folder): {dirpath} -> {new_dir}")
            shutil.move(dirpath, new_dir)


class Delete:
    """
    Delete class is responsible to delete any content
    """

    def __init__(self, file_list: list, folder_list: list) -> None:
        self.file_list = file_list
        self.folder_list = folder_list

    def files(self):
        """
        files method delete all files in delete files list
        """

        for pathfile in self.file_list:
            print(f"Deleting \"{pathfile}\" file")
            os.remove(f"{ROOT}/{pathfile}")

    def folders(self):
        """
        folders method delete all folders in delete folder list
        """

        for pathdir in self.folder_list:
            print(f"Deleting \"{pathdir}\" folder")
            shutil.rmtree(f"{ROOT}/{pathdir}")


def main():
    """
    main code execution
    """

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

    with open(sys.argv[1], "r", encoding="utf-8") as json_dict:
        replace_dict = Tool.generate_cases(json.loads(json_dict.read()))
        json_dict.close()

    main()

    print("Script ended successfully!")
