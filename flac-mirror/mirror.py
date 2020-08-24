#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# Mirror flac files to other formats.
#
# Files in FLAC_DIR are scanned to check if they have a 
# corresponding mirrored version in the other format *_DIR 
# directory.  If *_DIR is not set for a format then the FLAC_DIR
# is used.
#
# Supported target formats are:
#   OGG
#   M4A
#   MP3
#
# The selected formats to mirror are set with the environment 
# variable MIRROR, e.g. MIRROR=MP3,OGG
#
# The ffmpeg conversation options can be over-ridden here to 
# change the quality etc. e.g MP3_OPTIONS=....
#
from os import environ
import os.path
import sys
from os import walk
import time
import subprocess

#
# Check that the mirrored format exists for the flac file.  If
# not use ffmpeg to create a version of the required format.
#
def check_mirror_status(flac_file, mirror_format):
    #
    # Get the relative name of the file, e.g. 
    # ~/Music/flac/Artist-Album/01-track.flac -> Artist-Album/01-track
    #
    rel_name = os.path.relpath(flac_file,  flac_dir)[:-4]
    
    
    #
    # Workout the target mirrored file name.  If it doesn't exist
    # then make sure the target directory exists first.
    #
    # e.g Artist-Album/01-track -> ~/Music/mp3/Artist-Album/01-track.mp3
    #
    mirror_file_name = os.path.join(mirror_format['DIR'], "{}{}".format(rel_name, mirror_format['EXT'].lower()))
    if not os.path.isfile(mirror_file_name):
        mirror_dir_name = os.path.dirname(mirror_file_name)
        if not os.path.isdir(mirror_dir_name):
            os.makedirs(mirror_dir_name)
            # 
            # set permissions of this new directory as per that of the directory that the flac file is in
            #
            flac_file_dir = os.path.dirname(os.path.abspath(flac_file))
            os.chown(mirror_dir_name, os.stat(flac_file_dir).st_uid, os.stat(flac_file_dir).st_gid)
            perms = os.stat(flac_file_dir).st_mode & 0o777
            os.chmod(mirror_dir_name, perms)
            
        mirror_command = ['/usr/bin/ffmpeg', '-i', flac_file]
        mirror_command = mirror_command + mirror_format['OPTIONS']
        mirror_command.append(mirror_file_name)
        #
        # Convert the file, if there is an error then display
        # stdout/stderr from the subprocess.
        #
        result = subprocess.run(mirror_command, capture_output=True)
        if os.path.isfile(mirror_file_name):
            #
            # Set the permissions of the newly mirrored file to be the same as the 
            # flac file.
            #
            os.chown(mirror_file_name, os.stat(flac_file).st_uid, os.stat(flac_file).st_gid)
            perms = os.stat(flac_file).st_mode & 0o777
            os.chmod(mirror_file_name, perms)

        if result.returncode == 0:
            print ("Created {}".format(mirror_file_name))
            return 'MIRRORED'
        else:
            print ("Error creating {}".format(mirror_file_name), file=sys.stderr)
            print (result.stdout)
            print (result.stderr, file=sys.stderr)
            return 'ERROR'
            
    else:
        return 'EXISTS'

#
# Scan the FLAC_DIR looking for flac files to mirror.
#
def scan_flac_dir():
    print("Scanning {}".format(flac_dir))
    counts = {'FLAC':0}
    start_time = time.time()
    for (dirpath, dirnames, filenames) in walk(flac_dir):
        for f in filenames:
            if f.endswith('.flac'):
                counts['FLAC'] += 1
                flac_file = os.path.join(dirpath, f)
                
                for mirror_format in mirror_formats:
                    rc = check_mirror_status(flac_file, format_options[mirror_format])
                    cc = "{}_{}".format(mirror_format, rc)
                    if cc not in counts:
                        counts[cc] = 0
                    counts[cc] += 1
    print ("    Scanned {} flac files in {:6.3f} seconds".format(counts['FLAC'], time.time() - start_time))
    for mirror_format in mirror_formats:
        print ("    {} : {}".format(mirror_format, format_options[mirror_format]['DIR']))
        for c in ['MIRRORED', 'ERROR', 'EXISTS']:
            print ("        {:<8} : {}".format(c, counts.get("{}_{}".format(mirror_format, c), 0)))





if __name__ == "__main__":
    #
    # Check what, if any formats are required to be mirrored
    #
    mirror_formats = environ.get('MIRROR', '').strip().split(',')
    if mirror_formats[0] == '':
        mirror_formats.pop()
    if len(mirror_formats) == 0:
        print ("No formats to mirror to specified - nothing to do", flush=True)
        sys.exit(1)
        
    #
    # Check flac dir is good, can't do much if it isn't set
    #
    flac_dir = environ.get('FLAC_DIR', '/flac')
    if not os.path.isdir(flac_dir):
        print("FLAC_DIR '{}' is not an accessible directory".format(flac_dir), file=sys.stderr)
        sys.exit(1)


    #
    # Default options
    #
    format_options = {
        'M4A': {
            'OPTIONS':'-c:a aac -b:a 192k -vn', 
            'DIR': '/m4a',
            'EXT': 'm4a'
              
            },
        'MP3': { 
            'OPTIONS':'-c:a mp3 -ab 192k -map_metadata 0', 
            'DIR':'/mp3',
            'EXT':'mp3'
            },
        'OGG': { 
            'OPTIONS':'-c:a libvorbis',
            'DIR': '/ogg',
            'EXT':'ogg'
            }
        }

    #
    # See if anything has been over-ridden with environment variables
    #
    for fmat in format_options:
        ev = "{}_DIR".format(fmat)
        if ev in os.environ:
            ed = environ.get(ev) 
            if not os.path.isdir(ed):
                print("{}={} is not an accessible directory".format(ev, ed), file=sys.stderr, flush=True)
            else:
                format_options[fmat]['DIR'] = environ.get(ev) 
        eo = "{}_OPTIONS".format(fmat)
        if eo in os.environ:
            format_options[fmat]['OPTIONS'] = environ.get(eo) 
        format_options[fmat]['OPTIONS'] = format_options[fmat]['OPTIONS'].split(' ')
    
    #
    # Print the config
    #
    print ("flac-mirror")
    for fmat in format_options:
        if fmat not in mirror_formats:
            print ("    {} - not enabled".format(fmat))
        else:
            print ("    {}".format(fmat))
            print ("         DIR : {}".format(format_options[fmat]["DIR"]))
            print ("         EXT : {}".format(format_options[fmat]["EXT"]))
            print ("         OPTIONS : {}".format(format_options[fmat]["OPTIONS"]))
    print(flush=True)        
    
            
    #
    # Scan the flac dir looking for work.  Wait a minute before scanning again.
    #
    sleep_time = 60
    while (True):
        if len(mirror_formats) == 0:
            break
        scan_flac_dir()
        print ("Sleeping for {} seconds before re-scanning".format(sleep_time), flush=True)
        time.sleep(sleep_time)
