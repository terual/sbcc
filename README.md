SqueezeBox CopyCat (sbcc)
=========================

*   Use sbcc.py to run. If it does not find a sbcc.cfg file, it will 
    automatically create it. To rerun the setup, just delete the sbcc.cfg file.

*   This script mimics a Squeezebox on your network using the CLI interface to 
    your Squeezebox Server. It uses then flac, sox and a couple of other
    helper programs to playback the music. You should have the music mounted
    locally (NFS, samba, etc) or have a local Squeezebox Server instance.

*   This is created to be able to playback 192kHz (or even higher) files 
    using the Squeezebox Server framework to a computer running Linux.
