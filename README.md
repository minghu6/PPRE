Project Pokemon ROM Editor 2 (PPRE)

URL: ~~http://projectpokemon.org/ppre/~~
Origin Author: Alpha
Current Maintainer: minghu6

PPRE is a multi-purpose ROM editing tool for altering Nintendo DS Pokemon games.
The project was started originally to edit Pokemon Diamond and Pearl by SCV
based off of Treeki's Nitro Explorer and loadingNOW's thenewpoketext. pichu2000
created a strong basis for the scripting capabilities that PPRE will always
have. Alpha has added many new features to make PPRE as versatile as it is.
PPRE is written in Python and makes use of PyQt for its GUI. Development was led
by SCV and Alpha.

PPRE2 is a complete re-coring of PPRE. The original developers were still
immature in their programming practices, so there is a lot of room to grow. The
goal of PPRE2 is to provide a much better experience for ROM editing and to add
many new features. ~~Development is led by Alpha~~ Maintainment is dictated by minghu6 and open to the Project Pokemon community.

PPRE2 should be referred to as PPRE.

Requirements to run PPRE (Source Version):
* Python 3.x (=3.10)
* PyQt5
* Git

Current Game Support:
* Diamond (US)
* Pearl (US)
* Platinum (US)
* Heart Gold (US)
* Soul Silver (US)
* Black (US)
* White (US)
* Black2 (US)
* White2 (US)

Current Editors (incomplete):
* Pokemon Editor (Read/Write)
* Text Editor (RW)
* Move Editor (RW)

How to setup and use:
1. Run setup.sh/setup.bat
Or
1a. Use git to fetch the rawdb dependency (`git submodule update --init`)
1b. Link rawdb/nds to nds (or copy it if your OS does not have link support)

1. Run ppre.py
1. Create a new project (File > New Project, and select your base ROM)
Or
Just open an existed project folder (File > Open Folder, and select project folder)

1. Start Editing (Edit > Some editor), need save manually
1. Write your changes to a new ROM (File > Export Rom)

How to bundle:
1. install PyInstaller (`pip install pyinstaller`) (Don't install python through windows store!)
1. `pyinstaller pppre.spec`

How to make patch:
1. Export the new rom (File > Export Rom)
2. Make a patch (File > Make Patch, and select patch saving destination and name)

Note:
 1. Making patch needs a base rom, it's baisclly a copy of origin nds when new a project, naming with `base.nds` in the toplevel of the project folder.
 1. For Linux, Making patch needs install `xdelta3`
 1. For Non x86 Arch Linux, As Dumping nds needs `ndstool`, we have one precompiled x86 binary version on the directory `bin`, however, For the other arch users, they need replace with their version's `ndstool`, or their just open an existed dump directory.
