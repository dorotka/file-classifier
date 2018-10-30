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
"""

from argparse import ArgumentParser
from sys import stderr, stdout
from os import fsencode, listdir, fsdecode, path, rename, makedirs, remove
from pathlib import Path
import re
import subprocess
import datetime



argparser = ArgumentParser()
argparser.add_argument('from_dir',
    help='directory the images are in')

#todo: will move all this to config
base = 'base_path' # for photos
video_dir = 'movies_path' # for movies


def moveFiles(worklist, from_dir):
    """
    Move files to the correct directories based on date
    :return:
    """
    for file in worklist:
        filename = file[0]
        file_date = file[1]
        year = file_date.year
        month = file_date.strftime('%m')
        day = file_date.day
        print(month)
        to_dir = path.join(base, str(year), month, str(day))
        to = Path(to_dir)
        to_f = path.join(to_dir, filename)
        to_file = Path(to_f)
        print('to.isDir', to.is_dir())
        print('to.isFile', to_file.is_file())
        if not to.is_dir():
            makedirs(to_dir)
            print("made ", to_dir)
        if to_file.is_file():
            print("File already exists")
            continue
        rename(path.join(from_dir, filename), path.join(to_dir, filename))
        # rename(path.join(from_dir, filename), path.join(from_dir, "_bak_"+filename))
        # remove(path.join(from_dir, "_bak_"+filename))
        print("Moved ", path.join(from_dir, filename))
        break
        # print(to_dir, '\n')



def ask_confirmation(worklist):
    """
    print files to be moved and directories. Ask for confirmation -- if given, remove the backed files. Otherwise roll back.
    :param worklist:
    :return:
    """
    pass


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


def main():
    args = argparser.parse_args()
    if args.from_dir is None:
        stderr.write('from_dir is required!')
    worklist = set()
    pics = path.join(base, args.from_dir)
    # pics = fsencode(pics)
    # use ll command instead and separate the date
    # for file in listdir(pics):
    #     filename = fsdecode(file)
    #     print(filename, " ")
    #     completed = subprocess.run(['stat', filename], stdout=subprocess.PIPE, universal_newlines=True, cwd=pics)
    #     lines_str = str(completed.stdout)
    #     print(lines_str)
    completed = subprocess.run(['ls', '-lUh'], stdout=subprocess.PIPE, universal_newlines=True, cwd=pics)
    # completed = subprocess.run(['ls', '-lR', '|', 'akw', '{\'print $5" "$6" "$7" "$8" "$9\'}'], stdout=subprocess.PIPE, shell=True, universal_newlines=True, cwd=pics)
    lines_str = str(completed.stdout)
    lines = lines_str.split('\n')
    dir_date = get_dir_date(pics)
    # print(dir_date.month)
    size_regex = '[0-9]+(.[0-9]+)?(M|K|B|G)'
    for line in lines:
        size_pattern = re.compile(size_regex, re.IGNORECASE)
        temp = re.split(size_pattern, line)
        if len(temp) < 2:
            print('short list')
            continue
        meta = temp[-1]
        print(meta, '\n')
        file_date = get_meta_date(meta)
        filename = re.split(' +', meta.strip())[-1]
        if file_date != dir_date:
            worklist.add((filename, file_date))
    print(len(worklist))
    moveFiles(worklist, pics)
    stdout.write('DONE.')



if __name__ == '__main__':
    main()