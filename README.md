# Historical Twin

This software was written for the Tyree Photo Collection exhibit at the Nelson Provincial Museum, and I'm dumping the code online in case it'll be helpful for anyone else.

To run it requires OpenFace installed, which I've successfully tested the [installation instructions](http://cmusatyalab.github.io/openface/setup/#by-hand) on elementary OS and Ubuntu.

Once OpenFace is installed run  `describe_faces.py` over a directory of portrait photos you want Historical Twin to match visitors to. This may take a while, but once your done that directory would be configured to be loaded quickly into `magic_camera.py` or `magic_mirror.py` both of which alternative UIs for matching visitor faces to photos from the preconfigured collection.

You may also have to create a creditlines.tsv file which pairs filenames (excluding the 3 letter extension) in the first column to captions that should be displayed for the photo by `magic_camera.py` alongside the given photo.
