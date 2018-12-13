#!/usr/bin/env python3

"""
    Helper contains helper methods to deal with dates, directories creations, duplicate files and type distinctions.


Usage:
    to be included in the main classifier
"""
import configparser
import datetime
import re
import json
from sys import stderr
from os import fsencode, listdir, fsdecode, path, rename, makedirs, remove
from pathlib import Path


config = configparser.ConfigParser()
config.read('config.ini')
base = config['DEFAULT']['BASE'] # base dir for photos
video_dir = config['DEFAULT']['VIDEO_DIR'] # base dir for movies
size_regex = config['DEFAULT']['SIZE_REGEX'] # regex for size syntax


def convert_date_to_dir(date):
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')
    dir_str = path.join(base, str(year), month, str(day))
    dirs = {
        'to_dir' : dir_str,
        'to_dir_path' : Path(dir_str)
    }
    return dirs


def get_dir_date(dir):
    """
    Convert current directory into date. Example: somepath/Masters/2018/12/10 is 10 Dec 2018 (year/month/day).
    :param dir:
    :return: directory date
    """
    folders = path.normpath(dir).split(path.sep)
    #todo: figure out if the folder provides full date or beyond
    year = folders[-3]
    month = folders[-2]
    day = folders[-1]
    dir_date = datetime.datetime(int(year), int(month), int(day))
    return dir_date


def get_meta_date(meta):
    """
    Finds date attributes in a meta string and converts into date. It checks whether attributes contain year or time, if
    time found, the current system year is assumed.
    :param meta:
    :return:
    """
    meta_list = re.split(' +', meta.strip())
    month = meta_list[0]
    day = meta_list[1]
    year = datetime.datetime.now().year if meta_list[2].find(':') else meta_list[2]
    date_str = month + ' ' + str(day) + ' ' + str(year)
    return datetime.datetime.strptime(date_str, '%b %d %Y')


def get_filename(s):
    return re.split(' +', s.strip())[-1]


def split_on_size(line):
    size_pattern = re.compile(size_regex, re.IGNORECASE)
    return re.split(size_pattern, line)


def save_in_file(data, name, directory):
    """
    :param data: data to be saved
    :param name: file name with extension
    :param directory: directory to save file in
    """
    out_dir = directory
    makedirs(out_dir, exist_ok=True)
    try:
        with open(path.join(out_dir, name), 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)
    except Exception as e:
        stderr.write('E: error while trying to write the file: {}/{}\n'.format(directory, name))
        print(e)
    # logging.info('Saved file {}/{}\n'.format(directory, name))



