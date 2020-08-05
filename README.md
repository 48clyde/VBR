# VBR : VortexBox Replacement

A docker container based replacement for VortexBox, providing the core VortexBox functionality of:

* **LMS** - The Logitech Media Server that indexes and serves media files

* **SqueezeLite** - a local media player for playing music back through the local sound card

* **Ripper** - A CD ripper and tagger

that can easily be deployed via docker on an existing Linux based host system.


[VortexBox](https://wiki.vortexbox.org/what_is_vortexbox) is a Fedora based Linux distribution that turns an unused computer into a music server.  The server will automatically rip inserted CD's to FLAC format, ID3 tag the files and download cover art.  These files are then shared multiple ways on the local network such as via SAMBA file sharing as well as through the Logitech Media Server(LMS) to LMS compliant devices.

VortexBox provides a lot of functionality and has a lot of smarts to turn an old machine into a music server, from installing an operating system, configuring the machine, setting up the file system.  However the down side to this great functionality is the old version of the underlying OS being used limits the machine from being used for running other more contempory software and services.


## Pre-requisites

**Ubuntu**.  In theory your favourite 64bit Linux distribution should be suitable, as long as it can run docker. For developing VBR, Ubuntu 18.04 was used as the host computer OS for the docker server.

**docker community edition**. The client and server were both using version 18.09.7 of docker.  For the docker client and server installation instructions see [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

**docker-compose** [See Install Docker Compose](https://docs.docker.com/compose/install/) for instructions.  The version used was 1.26.2

**git** Install the git source code system for pulling down the VBR project from github where it is hosted
    
    sudo apt install git


## Installation

###Pull down the code from github for VBR

    git pull https://github.com/48clyde/VBR


### Confirm the settings

Check the default settings in the docker-compose.yml file.  Key items to check are:

* The location of the music files that LMS will serve and where the ripper will put the ripped FLAC files.  By default this is your Music directory.

* The sound output device used by SqueezeLite for playback, by default the first device on the first sound card.

* The CDROM device, see /proc/sys/dev/cdrom/info for the drive name

Other items of interest should all be well annotated and set with acceptable defaults.


### Building

The docker images need to be downloaded and built as per the definition in the docker-compose.yml file.  This may take a few minutes the first time they are built because the required components will not be cached locally and will need to be pulled down.  

    docker-compose --file=VBR/docker-compose.yml build

*NOTE* if you make changes to VBR/docker-compose.yml you will need to re-build.


### Start the containers

Start the docker compose group of containers as backgound processes.  By default they are configured to always restart (such as after a failure upon reboot) unless they've been explicitly stopped.

    docker-compose --file=~/VBR/docker-compose.yml up -d


### Stopping the containers

To stop all the VBR containers, use the command:

    docker-compose --file=~/VBR/docker-compose.yml stop
    
Note: They will remain stopped even after rebooting, you will need to start them again with the start command.


### Removing VBR

If you decide you don't want to use VBR, thanks to the magic of docker, you can stop and remove all these containers.  The LMS state directory where the database etc. that it builds is stored will need to be manually removed.

    docker-compose --file=~/VBR/docker-compose.yml down


### Troubleshooting

If things go wrong or are not working as expected, check that the containers are running and a review the logs for the containers.

To see the docker containers currently running:

    docker ps
    
    
To examine the logs of a running container:
 
    docker logs vbr_squeezelite_1
    
    
or to follow the tail on the logs:

    docker logs -f vbr_ripper_1

If you've made changes to any of the files such as docker-compose.yml, then the docker images will need to be re-built for the changes to be picked up.  So take down the containers to stop and remove them, build them again, then bring up the re-configured containers.


## Acknowledgements

Like all projects, 
