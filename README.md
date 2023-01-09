# MP3 Contents Hash

Sometimes you want to know if an MP3 file is already in your library.

A simple hash comparison is insufficient if your library is indexed by
a tool that modifies metadata on import (iTunes!). 

This utility solves that problem by hashing just the audio frames of the file.

TODO: Make it a proper module