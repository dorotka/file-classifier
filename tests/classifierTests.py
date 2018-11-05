#!/usr/bin/env python3
"""
    Set of unit tests for file-classifier.

    Usage: python3 -m unittest tests/classifierTests.py
"""

from os import path, rename
from pathlib import Path
import unittest
import classifier
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

class TestClassifierMethods(unittest.TestCase):

    def setUp(self):
        self.line = '-rwxrwxrwx     1 dorotka  staff   2.4M Mar 17  2015 GOPR2507.JPG'
        self.meta = ' Mar 17  2015 GOPR2521.JPG'
        self.directory = 'some/folder/structure/2018/02/12'
        self.directory_incomplete = 'some/folder/structure/2018/02'
        self.from_dir = config['TEST']['FROM_DIR'] # base dir for test photos
        self.base = config['DEFAULT']['BASE']
        # move file success
        to_date = datetime.datetime(2018, 9, 23)
        self.move_filename = 'DSC_0688.JPG'
        self.worklist = set()
        self.worklist.add((self.move_filename, to_date))
        self.to_file = path.join(self.base, '2018/09/23', self.move_filename)
        self.from_file = path.join(self.from_dir, self.move_filename)
        if not Path(self.from_file).is_file():
            if Path(self.to_file).is_file():
                rename(self.to_file, self.from_file)

    def test_split_on_size_m(self):
        tokens = classifier.split_on_size(self.line)
        self.assertEqual(tokens[-1].strip(), 'Mar 17  2015 GOPR2507.JPG', 'test_split_on_size M')

    def test_split_on_size_g(self):
        tokens = classifier.split_on_size(self.line)
        self.assertEqual(tokens[-1].strip(), 'Mar 17  2015 GOPR2507.JPG', 'test_split_on_size G')

    def test_split_on_size_k(self):
        tokens = classifier.split_on_size(self.line)
        self.assertEqual(tokens[-1].strip(), 'Mar 17  2015 GOPR2507.JPG', 'test_split_on_size K')

    def test_get_meta_date(self):
        date = datetime.datetime(2018, 3, 17)
        self.assertEqual(date, classifier.get_meta_date(self.meta), 'test_get_meta_date')

    def test_get_filename(self):
        self.assertEqual('GOPR2521.JPG', classifier.get_filename(self.meta), 'test_get_filename')

    def test_get_dir_date(self):
        date = datetime.datetime(2018, 2, 12)
        self.assertEqual(date, classifier.get_dir_date(self.directory), 'test_get_dir_date')

    def test_get_dir_date_incomplete(self):
        """Currently there is no functionality to deal with incomplete directories (like the one missing a day)"""
        with self.assertRaises(Exception):
            d = classifier.get_dir_date(self.directory_incomplete)

    def test_create_worklist(self):
        worklist = classifier.create_worklist(self.from_dir, None)
        self.assertEqual(1, len(worklist), 'test_create_worklist')

    def test_convert_date_to_dir(self):
        date = datetime.datetime(2018, 3, 24)
        dir = path.join(self.base, '2018/03/24')
        self.assertEqual(dir, classifier.convert_date_to_dir(date)['to_dir'])

    def test_move_file_removed(self):
        """Tests if the file that was moved is no longer in the from_dir"""
        #todo: will have to setup the file in directory before running
        classifier.moveFiles(self.worklist, self.from_dir)
        from_file_path = Path(self.from_file)
        self.assertFalse(from_file_path.is_file())

    def test_move_file_placed(self):
        """Test if the file that was moved was correctly palace in the right directory"""
        classifier.moveFiles(self.worklist, self.from_dir)
        to_file_path = Path(self.to_file)
        self.assertTrue(to_file_path.is_file())

    def test_move_file_exists(self):
        """Test moving file when the given file already exists in the to_dir.
        Currently, it will abort the move without any additional checks."""
        pass

    #todo: test that single digit months and days are saved as two digit folders like 6 -> 06

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()