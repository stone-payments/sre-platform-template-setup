from setup import *
from unittest.mock import patch, mock_open, Mock
import os
import unittest

IGNORE_FOLDERS = [
    "my/test",
]

IGNORE_EXTENSIONS = [
    ".test",
]

DELETE_FILES = [
    "delete-me.txt"
]

DELETE_FOLDERS = [
    "delete-me"
]

DESIRED_DICT = {
  "my-test": "my-great-test", 
  "my_test": "my_great_test", 
  "MyTest": "MyGreatTest", 
  "myTest": "myGreatTest"
}

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

    folder = f"{os.path.normpath('test-files')}/my/test/waw"
    result = is_ignored_folder(IGNORE_FOLDERS, folder, 'test-files')

    self.assertTrue(result)

  def test_folder_not_match(self):
    """
    Folder not match with some item in folder ignore list
    """

    folder = f"{os.path.normpath('test-files')}/candy/my/test/waw"
    result = is_ignored_folder(IGNORE_FOLDERS, folder, 'test-files')

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

    path = "/test-files/my-test.txt"
    
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
      with patch('setup.is_any_item_in_string') as mock_method:
        mock_method.get.side_effect = False
        replace_file_content(DESIRED_DICT, path)
        mock_file.mock_calls[0].assert_called_once_with(path, 'r', errors='surrogateescape', encoding="utf-8")
        mock_file.mock_calls[4].assert_called_once_with(path, 'w', encoding="utf-8")

class TestReplaceFileName(unittest.TestCase):
  def test_rename_file_name(self):
    """
    Verifies if file has been renamed to desired name
    """

    with patch('os.rename') as mock_rename:
      with patch('setup.is_any_item_in_string') as mock_method:
        mock_method.get.side_effect = False
        rename_file(DESIRED_DICT, "my-test.txt", "/test-files")
        mock_rename.assert_called_once_with('/test-files/my-test.txt', '/test-files/my-great-test.txt')


class TestReplaceFolderName(unittest.TestCase):
  def test_rename_folder_name(self):
    """
    Verifies if folder name has been renamed
    """
    
    with patch('os.walk') as mock_walk:
      with patch('shutil.move') as mock_move:
        with patch('setup.is_ignored_folder') as mock_ignore_folder:
          with patch('setup.is_any_item_in_string') as mock_has_string:
            mock_ignore_folder.return_value = False
            mock_has_string.return_value = True
            mock_walk.return_value = [('/test-files/my-test', ('test',), ('test',))]
            rename_folder(DESIRED_DICT, "/test-files/my-test", IGNORE_FOLDERS)
            mock_move.assert_called_with('/test-files/my-test', '/test-files/my-great-test')

class TestDeleteFiles(unittest.TestCase):
  def test_delete_files(self):
    """
    The desired file must be deleted
    """

    with patch('os.remove') as mock_remove:
      delete_files(DELETE_FILES, 'test-files')
      mock_remove.assert_called_with('test-files/delete-me.txt')

class TestDeleteFolder(unittest.TestCase):
  def test_delete_folder(self):
    """
    The desired folder must be deleted
    """

    with patch('shutil.rmtree') as mock_remove:
      delete_folders(DELETE_FOLDERS, 'test-files')
      mock_remove.assert_called_with('test-files/delete-me')


class TestMain(unittest.TestCase):
  def test_main(self):
    """
    The main execution need run as expected
    """
    root = 'testing'
    with patch('os.walk') as mock_walk:
      with patch('os.chdir') as mock_chdir:
        with patch('setup.is_ignored_folder') as mock_ignored_folder:
          with patch('setup.is_ignored_extension') as mock_ignored_extension:
            with patch('setup.replace_file_content') as mock_replace_content:
              with patch('setup.rename_folder') as mock_rename_file:
                with patch('setup.delete_files') as mock_delete_files:
                  with patch('setup.delete_folders') as mock_delete_folders:
                    mock_walk.return_value = [('/test-files/my-test', ('test',), (['test']))]
                    mock_ignored_folder.return_value = False
                    mock_ignored_extension.return_value = False

                    main(DESIRED_DICT, root)
                    
                    mock_chdir.assert_called_once()
                    mock_ignored_folder.assert_called()
                    mock_ignored_extension.assert_called()
                    mock_replace_content.assert_called()
                    mock_rename_file.assert_called()
                    mock_delete_files.assert_called()
                    mock_delete_folders.assert_called()
      

if __name__ == '__main__':
  unittest.main()