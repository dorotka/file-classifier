# file-classifier
Simple script to classify photos by date.

## What it does
It checks if all the files in the selected directory were created on the correct date, if not, the files are moved to a proper directory.
Currently it assumes year/month/day directory structure.

## Why?
Do you actually care for you mobile photos? Do you download and archive them on you Mac? 
No, because you're tired of the fact that Macs will throw a year of pics into one folder that is too large to traverse by hand. 
This script, allows you to classify those photos into separate folders based on photo creation date. Much easier, much more neat.

## Q&A
1. 
Q: When I run the script I get the "Operation not permitted error".  
A: If you recently installed Mac OS Mojave, your permissions have changed. In order to allow execution of this and any other script in the Terminal (or terminal-like app you use) you need to grant it full disk access. Please follow instruciton here:
[fix-operation-not-permitted-terminal](http://osxdaily.com/2018/10/09/fix-operation-not-permitted-terminal-error-macos/)
