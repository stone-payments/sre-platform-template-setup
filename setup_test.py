import os
import unittest

TARGET = __import__("setup.py")

ROOT    = os.environ["GITHUB_WORKSPACE"]
TOOL    = TARGET.Tool
IGNORE  = TARGET.Ignore
REPLACE = TARGET.Replace

IGNORE_FOLDERS = [
    "my/test",
]

IGNORE_EXTENSIONS = [
    ".test",
]

class TestToolAnyItemInString(unittest.TestCase):
  def has_item_in_string(self):
    """
    Has item in string and should return true
    """

    items = ["potato", "test", "pineapple"]
    string = "I love pineapple!"
    result = TOOL.is_any_item_in_string(items, string)

    self.assertTrue(result)

  def no_has_item_in_string(self):
    """
    No has item in string and should return false
    """

    items = ["potato", "test", "pineapple"]
    string = "I love strawberry!"
    result = TOOL.is_any_item_in_string(items, string)

    self.assertFalse(result)

class TestToolGenerateCases(unittest.TestCase):
  def generate_cases(self):
    """
    Generate word cases in dictionary (kebab-case, pascalCase, snake_case, camelCase)
    """

    test_dict = {
      "i-love-potato": "i-love-candy"
    }

    expect_dict = {
      "i-love-potato": "i-love-candy",
      "ILovePotato": "ILoveCandy",
      "i_love_potato": "i_love_candy",
      "iLovePotato": "iLoveCandy",
    }

    result = Tool.generate_cases(test_dict)

    self.assertDictEqual(result, expect_dict)

class TestIgnoreFolderMatch(unittest.TestCase):
  def folder_really_match(self):
    """
    Folder match with some item in folder ignore list
    """

    folder = f"{os.path.normpath(ROOT)}/my/test/waw"
    result = IGNORE.folder_match(folder)

    self.assertTrue(result)

  def folder_not_match(self):
    """
    Folder not match with some item in folder ignore list
    """

    folder = f"{os.path.normpath(ROOT)}/candy/my/test/waw"
    result = IGNORE.folder_match(folder)

    self.assertFalse(result)

class TestIgnoreFileExtensionMatch(unittest.TestCase):
  def file_extension_really_match(self):
    """
    File extension match with some item in extension ignore list
    """

    ext = "candy.test"
    result = IGNORE.file_extension_match(ext)

    self.assertTrue(result)

  def file_extension_not_match(self):
    """
     File extension not match with some item in extension ignore list
    """

    ext = "candy.tasty"
    result = IGNORE.file_extension_match(ext)

    self.assertFalse(result)

class TestReplaceReplace(unittest.TestCase):
  def replace(self):
    """
    Verify if replace method just replace one string to another string
    """

    replace_dict = {
      "my-test": "my-great-test",
      "my_test": "my_great_test",
      "MyTest": "MyGreatTest",
      "myTest": "myGreatTest"
    }

    replacing = REPLACE(replace_dict)
    test_content = "some word my-test, become my_test... but i prefer MyTest or myTest!"
    expect_content = "some word my-great-test, become my_great_test... but i prefer MyGreatTest or myGreatTest!"
    result = replacing.replace(test_content)

    self.assertEqual(result, expect_content)

class TestReplaceFileContent(unittest.TestCase):
  pass