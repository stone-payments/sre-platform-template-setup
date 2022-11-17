from setup import *
from pathlib import Path
import os
import unittest

IGNORE_FOLDERS = [
    "my/test",
]

IGNORE_EXTENSIONS = [
    ".test",
]

DELETE_FILES = [
    "test-files/delete-me.txt"
]

DELETE_FOLDERS = [
    "test-files/delete-me"
]

DESIRED_DICT = {
  "my-test": "my-great-test", 
  "my_test": "my_great_test", 
  "MyTest": "MyGreatTest", 
  "myTest": "myGreatTest"
}

ROOT = os.environ["GITHUB_WORKSPACE"]

class TestAnyItemInString(unittest.TestCase):
  def test_has_item_in_string(self):
    """
    Has item in string and should return true
    """

    items = ["potato", "test", "pineapple"]
    string = "I love pineapple!"
    result = is_any_item_in_string(items, string)

    self.assertTrue(result)

  def test_no_has_item_in_string(self):
    """
    Hasn't any item in string and should return false
    """

    items = ["potato", "test", "pineapple"]
    string = "I love strawberry!"
    result = is_any_item_in_string(items, string)

    self.assertFalse(result)


class TestGenerateCases(unittest.TestCase):
  def test_generate_cases(self):
    """
    Generate word cases in dictionary (kebab-case, pascalCase, snake_case, camelCase)
    """

    test_dict = {
      "love-potato": "love-candy"
    }

    expect_dict = {
      "love-potato": "love-candy",
      "LovePotato": "LoveCandy",
      "love_potato": "love_candy",
      "lovePotato": "loveCandy",
    }

    result = generate_cases(test_dict)

    self.assertDictEqual(result, expect_dict)


class TestIgnoreFolderMatch(unittest.TestCase):
  def test_folder_really_match(self):
    """
    Folder match with some item in folder ignore list
    """

    folder = f"{os.path.normpath(ROOT)}/my/test/waw"
    result = is_ignored_folder(IGNORE_FOLDERS, folder)

    self.assertTrue(result)

  def test_folder_not_match(self):
    """
    Folder not match with some item in folder ignore list
    """

    folder = f"{os.path.normpath(ROOT)}/candy/my/test/waw"
    result = is_ignored_folder(IGNORE_FOLDERS, folder)

    self.assertFalse(result)


class TestIgnoreFileExtensionMatch(unittest.TestCase):
  def test_file_extension_really_match(self):
    """
    File extension match with some item in extension ignore list
    """

    ext = "candy.test"
    result = is_ignored_extension(IGNORE_EXTENSIONS, ext)

    self.assertTrue(result)

  def test_file_extension_not_match(self):
    """
     File extension not match with some item in extension ignore list
    """

    ext = "candy.tasty"
    result = is_ignored_extension(IGNORE_EXTENSIONS, ext)

    self.assertFalse(result)


class TestReplace(unittest.TestCase):
  def test_replace(self):
    """
    Verify if replace method just replace one string to another string
    """

    test_content = "some word my-test, become my_test... but i prefer MyTest or myTest!"
    expect_content = "some word my-great-test, become my_great_test... but i prefer MyGreatTest or myGreatTest!"
    result = replace(DESIRED_DICT, test_content)

    self.assertEqual(result, expect_content)


class TestReplaceFileContent(unittest.TestCase):
  def test_specific_word_change_in_content_file(self):
    """
    The desired word in file content need be changed ("my-test")
    """

    path = "test-files/my-test.txt"
    expect_content = "THIS WORD NEED BE CHANGED BY test.py -> my-great-test."
    replace_file_content(DESIRED_DICT, path)
    
    with open(path,'r',errors='surrogateescape') as file:
      result = file.read()
      self.assertEqual(result, expect_content)


class TestReplaceFileName(unittest.TestCase):
  def test_rename_file_name(self):
    """
    Verifies if file has been renamed to desired name
    """

    rename_file(DESIRED_DICT, "my-test.txt", "test-files")
    validateTest = os.path.exists("test-files/my-great-test.txt")

    self.assertTrue(validateTest)


class TestReplaceFolderName(unittest.TestCase):
  def test_rename_folder_name(self):
    """
    Verifies if folder name has been renamed
    """

    rename_folder(DESIRED_DICT, "test-files/my-test", IGNORE_FOLDERS)
    validateTest = os.path.exists("test-files/my-great-test")

    self.assertTrue(validateTest)


class TestDeleteFiles(unittest.TestCase):
  def test_delete_files(self):
    """
    The desired file must be deleted
    """

    delete_files(DELETE_FILES)
    validateTest = os.path.exists("test-files/delete-me.txt")

    self.assertFalse(validateTest)


class TestDeleteFolder(unittest.TestCase):
  def test_delete_folder(self):
    """
    The desired folder must be deleted
    """

    delete_folders(DELETE_FOLDERS)
    validateTest = os.path.exists("test-files/delete-me")

    self.assertFalse(validateTest)


class TestMain(unittest.TestCase):
  def test_main(self):
    """
    The main execution need run as expected
    """

    fails = []
    main(DESIRED_DICT, "./main-test")

    with open('main-test/checkContent.txt','r',errors='surrogateescape') as file:
      content_result = file.read()

    checks = {
      "ignore": {
        "folder": os.path.exists("main-test/.github/my-test.txt"),
        "extension": os.path.exists("main-test/my-test.svg")
      },
      "delete": {
        "file": not os.path.exists("main-test/.github/workflows/repo-setup.yml"),
        "folder": not os.path.exists("main-test/.setup")
      },
      "replace": {
        "content": content_result == "my-great-test",
        "file_name": os.path.exists("main-test/my-great-test.txt"),
        "folder_name": os.path.exists("main-test/my-great-test")
      }
    }

    for topics, results in checks.items():
      for chall, success in results.items():
        if not success:
          fails.append(f"Failed in {topics} -> {chall}")
    
    if len(fails) > 0:
      for fail in fails: print(fail)
      self.assertTrue(False)
    
    self.assertTrue(True)


if __name__ == '__main__':
  unittest.main()