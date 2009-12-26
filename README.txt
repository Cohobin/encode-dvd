Encode DVD 1.0 (Build 42) by Robert M. Pufky (robert.pufky@gmail.com)
11/23/2009

Encode DVD was born from the need to encode lots of DVD's without the hassle of
manually processing them through the GUI.  Core code on Encode DVD was completed
in a month, working mostly in 1-2 hour blocks at night.

Of course, HandBrake 0.9.4 was released as soon as I release this, so expect a
updated version of encode-dvd to support 0.9.4 shortly.

This readme will show you how to install Encode DVD on your system.  Once
installed, just run encode-dvd --help for encoding instructions.

Works on both Linux and OSX.

Requirements:
-------------
python 2.5
mox 0.5.1
handbrakeCLI (0.9.3)

Basic Installation:
-------------------
1) create the following directories:
  sudo mkdir -p /etc/encode-dvd
  sudo mkdir -p /opt/bin/encode-dvd/1.0
  sudo mkdir -p /var/log/encode-dvd
  sudo mkdir -p /opt/bin

2) Move encode-dvd to source directory
  mv * /opt/bin/encode-dvd/1.0/

3) Copy the configuration file to /etc/encode-dvd
  cp /opt/bin/encode-dvd/1.0/encode_dvd.config /etc/encode-dvd/

4) symlink encode-dvd to /opt/bin
  ln -s /opt/bin/encode-dvd/1.0/encode_dvd.py /opt/bin/encode-dvd 

5) Ensure your path contains /opt/bin
  PATH=$PATH:/opt/bin

Testing:
--------
1) Download mox from http://pymox.googlecode.com/files/mox-0.5.1.tar.gz
2) Extract to some location, cd to that directory
3) Install mox http://code.google.com/p/pymox/wiki/MoxDocumentation
  python setup.py install
4) cd /opt/bin/encode-dvd/1.0
5) Run test
   ./full_test.py
6) All tests should pass

HandBrake:
----------
The python handbrake library included in encode-dvd, it expects to find the
binary 'HandBrakeCLI' in one of these paths:
- /usr/bin
- /usr/local/bin
- /bin
- /opt/bin

If it is not in one of these locations, just symlink HandBrakeCLI to one of
these locations.

Use your package manager to install handbrake, or download and manually
build/install handbrake (http://handbrake.fr/downloads.php)
If you don't have the binary installed, you can search the internet and download
a HandBrake package to install, or use your linux package manager.