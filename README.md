# Rai3PodcastRenamer
Rai3 podcast renamer. Simple program that: chooses folder and recursively renames al files of the form:
     
     <channel>_del_dd_mm_yyyy_<episode title>
     
to:

     yyyy_mm_dd_<episode title>_<channel>

this is useful for some podcasts that adopt the above mentioned braindead scheme.


## Usage

Just run the program.

## Implementation
Written in python. For convenience, a windows executable generated with pyinstaller is provided in the 'dist' folder
Actually a thin wrapper on a regexp.
