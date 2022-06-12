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

	# If it couldn't find the album in CDDB (or whatever's configured
	# in abcde-local.conf), it'll create an Unknown_Artist/Unkown_Album directory.
	# Then the *next one* like that will overwrite files in there.
	# So move it to someplace unique.  The pattern match here is intended
	# to support both my convention (directory per artist) and the default.
	#
	# It's handy that we haven't been able to eject yet :)
	# Taken from https://unix.stackexchange.com/a/287851
	#
	# From a workflow standpoint, it might be better to just use datetime;
	# I stack my CDs in the order I rip, so being able to sort by time
	# might work better when tagging. But since LMS/New Music sorts that
	# way anyway, let's go with a clean key. Since we've inherited
	# underscores munge the id to replace spaces with underscores. Do I
	# really want underscores?  I didn't have them in vbox.
	#
	# Don't have a clean way to make this respond to custom munge...
	# functions in abcde.conf. Hmm.
	dest_dir="/out/flac"
	if [ -d "${dest_dir}/Unknown_Artist/Unknown_Album" ]; then
	    disc_id=$(cd-discid /dev/sr0 | tr ' ' '_')
	    cd "${dest_dir}"
	    mv "Unknown_Artist/Unknown_Album" "Unknown_Artist/Unknown_Album_$disc_id"
	    cd "${OLDPWD}"
	fi
        
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
