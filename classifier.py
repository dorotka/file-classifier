#!/usr/bin/env python3

"""
WORK IN PROGRESS. Simple script to segregate media files in a folder. At this point, it requires the path to the folder that is supposed to be segragated from
the base directory (Masters in the example).
It gets data on all the files, and if a file does not belong in the given month/day directory, the file is moved.
It assumes the following folder strucrue: year/month/day.

Usage:
    python3 file_classifier.py <from_dir>
"""

from argparse import ArgumentParser
from sys import stderr, stdout
from os import path, rename, makedirs
from pathlib import Path
from helper import convert_date_to_dir, get_dir_date, get_filename, get_meta_date, split_on_size, save_in_file
import subprocess
import configparser
import time


argparser = ArgumentParser()
argparser.add_argument('from_dir',
    help='directory the images are in')

config = configparser.ConfigParser()
config.read('config.ini')
base = config['DEFAULT']['BASE'] # base dir for photos
video_dir = config['DEFAULT']['VIDEO_DIR'] # base dir for movies
size_regex = config['DEFAULT']['SIZE_REGEX'] # regex for size syntax
SUMMARY_PRINT_LIMIT = 50


def print_summary(worklist, dir):
    print("SUMMARY")
    print("Moved", len(worklist), "files.")
    if len(worklist) > SUMMARY_PRINT_LIMIT:
        name = 'moved_' + str(time.time()) + '.json'
        serl = ["Moved " + x[0] + " to " + str(convert_date_to_dir(x[1])['to_dir']) for x in worklist]
        save_in_file(serl, name, dir)
    else:
        for item in worklist:
            print(item[0], "was moved to ", item[1])


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


def create_worklist(pics, dir_date, worklist):
    """
    Goes over directories and adds files to the worklist if in a wrong place.
    :return:
    """
    # todo: in order not to go over moved files when we do recurvide over inner directories over different days,
    # we should first get all the files in the worklist over different directories, and then move in separate method
    # todo: could be a map as {to_date: [files]}
    print(pics)
    completed = subprocess.run(['ls', '-lUh'], stdout=subprocess.PIPE, universal_newlines=True, cwd=pics)
    lines_str = str(completed.stdout)
    lines = lines_str.split('\n')
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
    print_summary(worklist, '.')


def check_files(from_dir):
    pics = path.join(base, from_dir)
    # TODO: check if directory exists?
    dir_date = get_dir_date(pics)
    worklist = set()
    create_worklist(pics, dir_date, worklist)
    classify_files(pics, worklist)
    stdout.write('DONE')


def main():
    args = argparser.parse_args()
    if args.from_dir is None:
        stderr.write('from_dir is required!')
    check_files(args.from_dir)




if __name__ == '__main__':
    main()