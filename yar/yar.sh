#!/bin/bash
#
# yar - yet another ripper
#
#
# Check if there is an 'audio' type disc in the drive and if 
# so, rip it using abcde, then tell LMS to rescan the library
# and eject the disc.
#
# Then wait for the next disk to be inserted.
#


while true; do
    #
    # Check the state of the cd drive with setcd, that doesn't 
    #  try and close the drive if it is open etc.
    #
    DRIVE_STATE=`setcd -i ${CDROM} | head -2 | tail -1`
    # The drive state returned can be one of:
    #   CD tray is open
    #   No disc is inserted
    #   Drive is not ready
    #   Disc found in drive: audio disc
    #   Disc found in drive: data disc type 1
    #   Disc found in drive: mixed type CD (data/audio)

    if [[ $DRIVE_STATE =~ "audio" ]];then
        #
        # rip the cd
        #   -N non-interactive
        #   -d device
        #   -o output format(s)
        #   note - don't get abcde to eject the cd because /usr/bin/eject
        #   throws an error 'unable to eject, last error: Inappropriate ioctl for device'
        #   when run from the container.  Perhaps because the host system outside the
        #   container has mounted it or something?
        #
        # /etc/abcde-local.conf has a post_encode defined for
        # some post processing that sets the owner and group
        #
        #
        /usr/bin/abcde -N -d ${CDROM} -o flac -c /etc/abcde-local.conf
        
        #
        # Tell LMS to rescan the library to pick-up these new files
        #
        echo rescan | nc -C -q 1 ${LMS_HOST:-127.0.0.1} ${LMS_CLI_PORT:-9090}
        
        #
        # use sdparam to eject the disk
        # https://github.com/rix1337/docker-ripper/issues/3
        #
        sleep 2
        sdparm --quiet --command=unlock /dev/sr0
        sleep 1
        sdparm --quiet --command=eject /dev/sr0
    fi
        
    #
    # Nothing in the drive or not an audio disc, so check again
    # in a bit
    #
    sleep 2
    
done
