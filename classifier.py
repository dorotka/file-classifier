#!/usr/bin/env python3

"""
WORK IN PROGRESS. Simple script to segregate media files in a folder. At this point, it requires the path to the folder that is supposed to be segragated from
the base directory (Masters in the example).
It gets data on all the files, and if a file does not belong in the given month/day directory, the file is moved.
It assumes the following folder strucrue: year/month/day.

Features to come:
- distinguishing between video, photo and other extensions, (2)
- Configurable folder structure,
- Check if exact file exists before moving over -- not just name but size and date modified
- Allow to select month or year not just day folders (1)
- Go over files in the nested folder (0)
- While confirming, if the user does not accept all, allow to exclude specific files from the list.
- Scan functionality: pick a year or a month directory, the scan will go over all the files and folders inside
    and will give you a list of files that are in wrong directories. Maybe just print to console if certain size, if
    larger than write to a file.
- Scan after work done: Once directory is classified, do a scan of that directory.
"""

from argparse import ArgumentParser
from sys import stderr, stdout
from os import fsencode, listdir, fsdecode, path, rename, makedirs, remove
from pathlib import Path
import re
import subprocess
import configparser
import datetime


argparser = ArgumentParser()
argparser.add_argument('from_dir',
    help='directory the images are in')

config = configparser.ConfigParser()
config.read('config.ini')
base = config['DEFAULT']['BASE'] # base dir for photos
video_dir = config['DEFAULT']['VIDEO_DIR'] # base dir for movies
size_regex = config['DEFAULT']['SIZE_REGEX'] # regex for size syntax


def moveFiles(worklist, from_dir):
    """
    Move files to the correct directories based on date
    :return:
    """
    for file in worklist:
        filename = file[0]
        file_date = file[1]
        dirs = convert_date_to_dir(file_date)
        to_file = path.join(dirs['to_dir'], filename)
        to_file_path = Path(to_file)
        if not dirs['to_dir_path'].is_dir():
            makedirs(dirs['to_dir'])
            print("made ", dirs['to_dir'])
        if to_file_path.is_file():
            print("File already exists", filename)
            #todo: will have to deal with it to somehow mark them otherwise we will always be going though those files and never moving them
            #todo: will need to figure out whether really the same, then remove from source, if not rename and move
            continue
        rename(path.join(from_dir, filename), path.join(dirs['to_dir'], filename))
        #todo: remove from worklist after successful move
        print("Moved ", path.join(from_dir, filename), "to ", dirs['to_dir'])
        # todo: remove break after more testing
        break


def convert_date_to_dir(date):
    year = date.year
    month = date.strftime('%m')
    day = date.day
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


def create_worklist(pics, dir_date):
    """
    Goes over directories and adds files to the worklist if in a wrong place.
    :return:
    """
    # todo: in order not to go over moved files when we do recurvide over inner directories over different days,
    # we should first get all the files in the worklist over different directories, and then move in separate method
    # todo: could be a map as {to_date: [files]}
    worklist = set()
    print(pics)
    completed = subprocess.run(['ls', '-lUh'], stdout=subprocess.PIPE, universal_newlines=True, cwd=pics)
    lines_str = str(completed.stdout)
    lines = lines_str.split('\n')
    dir_date = get_dir_date(pics) if dir_date is None else dir_date
    for line in lines:
        tokens = split_on_size(line)
        if len(tokens) < 2:
            print('short list')
            continue
        meta = tokens[-1]
        file_date = get_meta_date(meta)
        filename = get_filename(meta)
        # if path.isdir(path.join(pics, filename)): # if a directory, recurse
        #     pass
        if file_date != dir_date:
            worklist.add((filename, file_date))
    print(len(worklist))
    return worklist


def classify_files(pics, worklist):
    """
    Gets the worklist of the files to move and moves them.
    It will also perform a "check scan" after moving files in the future.
    :return:
    """
    moveFiles(worklist, pics)


def check_files(from_dir):
    pics = path.join(base, from_dir)
    # TODO: check if directory exists?
    worklist = create_worklist(pics, None)
    classify_files(pics, worklist)
    stdout.write('DONE')


def main():
    args = argparser.parse_args()
    if args.from_dir is None:
        stderr.write('from_dir is required!')
    check_files(args.from_dir)




if __name__ == '__main__':
    main()