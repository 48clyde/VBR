####!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# Mirror flac files to other formats.
#
# Files in FLAC_DIR are scanned to check if they have a 
# corresponding mirrored version in the other format *_DIR 
# directory, if the *_DIR format directory environment variable 
# is set.
#
# Supported target formats are:
#   OGG
#   M4A
#   MP3
#

from os import environ
import os.path
import sys
from os import walk
import time
import subprocess


#
# Check if the directory specified exists
#
def check_dir(fmat):
    fdir = "{}_DIR".format(fmat)
    if fdir not in os.environ:
        return None

    fmt_mirror_dir = environ.get(fdir)
    if not os.path.isdir(fmt_mirror_dir):
        print("Env var {}={} is not an accessible directory".format(fdir, fmt_mirror_dir), file=sys.stderr)
        return None

    return (fmat, fmt_mirror_dir)


#
# Check that the mirrored format exists for the flac file.  If
# not use ffmpeg to create a version of the required format.
#
def check_mirror_status(flac_file, mirror_format):
    #
    # Get the relative name of the file, e.g. 
    # ~/Music/flac/Artist-Album/01-track.flac -> Artist-Album/01-track
    #
    rel_name = os.path.relpath(flac_file,  FLAC[1])[:-4]
    
    
    #
    # Workout the target mirrored file name.  If it doesn't exist
    # then make sure the target directory exists first.
    #
    # e.g Artist-Album/01-track -> ~/Music/mp3/Artist-Album/01-track.mp3
    #
    mirror_file_name = os.path.join(mirror_format[1], "{}{}".format(rel_name, mirror_format[0].lower()))
    if not os.path.isfile(mirror_file_name):
        mirror_dir_name = os.path.dirname(mirror_file_name)
        if not os.path.isdir(mirror_dir_name):
            os.makedirs(mirror_dir_name)
            os.chown(mirror_dir_name, int(environ.get('USER_ID', 1000)), int(environ.get('GROUP_ID', 1000)))
                

        mirror_command = ['/usr/bin/ffmpeg', '-i', flac_file]
        mirror_command = mirror_command + conversion_options[mirror_format[0]]
        mirror_command.append(mirror_file_name)
        #
        # Convert the file, if there is an error then display
        # stdout/stderr from the subsprocess.
        #
        result = subprocess.run(mirror_command, capture_output=True)
        if os.path.isfile(mirror_file_name):
            os.chown(mirror_file_name, int(environ.get('USER_ID', 1000)), int(environ.get('GROUP_ID', 1000)))

        if result.returncode == 0:
            print ("Created {}".format(mirror_file_name))
            return 'MIRRORED'
        else:
            print ("Error creating {}".format(mirror_file_name), file=sys.stderr)
            print (result.stdout)
            print (result.stderr, file=sys.stderr)
            return 'ERROR'
        print ("Changing ownership to {}:{}".format(int(environ.get('USER_ID', 998)), int(environ.get('GROUP_ID', 998))))
            
    else:
        return 'EXISTS'

#
# Scan the FLAC_DIR looking for flac files to mirror.
#
def scan_flac_dir():
    print("Scanning {}".format(FLAC[1]))
    counts = {'FLAC':0}
    start_time = time.time()
    for (dirpath, dirnames, filenames) in walk(FLAC[1]):
        for f in filenames:
            if f.endswith('.flac'):
                counts['FLAC'] += 1
                flac_file = os.path.join(dirpath, f)
                
                for mirror_format in mirror_formats:
                    rc = check_mirror_status(flac_file, mirror_format)
                    cc = "{}_{}".format(mirror_format[0], rc)
                    if cc not in counts:
                        counts[cc] = 0
                    counts[cc] += 1
    print ("    Scanned {} flac files in {:6.3f} seconds".format(counts['FLAC'], time.time() - start_time))
    for mirror_format in mirror_formats:
        print ("    {} : {}".format(mirror_format[0],mirror_format[1]))
        for c in ['MIRRORED', 'ERROR', 'EXISTS']:
            print ("        {:<8} : {}".format(c, counts.get("{}_{}".format(mirror_format[0], c), 0)))


if __name__ == "__main__":
    #
    # Check flac dir is good, can;t do much if it isn't set
    #
    FLAC = check_dir('FLAC')
    if FLAC is None:
        print("Env var FLAC_DIR not set", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.isdir(FLAC[1]):
        print("Env var FLAC_DIR '{}' is not an accessible directory".format(FLAC[1]), file=sys.stderr)
        sys.exit(1)


    #
    # The ffmpeg conversion commands.  Would probably be better in a config file
    #
    conversion_options = {
        'MP3':['-c:a', 'mp3', '-ab', '192k', '-map_metadata', '0'],
        'OGG':['-c:a', 'libvorbis'],
        'M4A':['-c:a', 'aac', '-b:a', '192k', '-vn']
    }
    
    #
    # Look to see what mirror formats are required
    #
    mirror_formats = []
    for rf in conversion_options:
        cd = check_dir(rf)
        if cd:
            mirror_formats.append(check_dir(rf))
        
    if len(mirror_formats) == 0:
        print("No output format directories specified, need to set one of MP3_DIR, OGG_DIR or M4A_DIR", file=sys.stderr)
        sys.exit(1)
        
    #
    # Scan the flac dir looking for work.  Wait a minute before scanning again.
    #
    sleep_time = 60
    while (True):
        scan_flac_dir()
        print ("Sleeping for {} seconds before re-scanning".format(sleep_time), flush=True)
        time.sleep(sleep_time)
