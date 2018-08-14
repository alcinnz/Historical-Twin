#! /usr/bin/python2
# Analyzes all faces in a directory using OpenFace and saves an index for the other scripts.
import sys, os, time
start = time.time()
import pygame, numpy, dlib
import recognition

index = recognition.MultiBinaryTree()
def find_faces(pygame_capture):
    capture = numpy.array(pygame.surfarray.pixels3d(pygame_capture))
    capture = numpy.swapaxes(capture, 0, 1)
    return recognition.align.getAllFaceBoundingBoxes(capture), capture

imgdir = sys.argv[1] if len(sys.argv) > 1 else "."
thumbIndex = 0
with open(os.path.join(imgdir, "index.tsv"), "w") as index:
    try:
        os.mkdir(os.path.join(imgdir, "thumbnails"))
    except Exception, e: pass

    for img in os.listdir(imgdir):
        imgpath = os.path.join(imgdir, img)
        print time.time() - start, imgpath
        try:
            photo = pygame.image.load(imgpath)
            faces, photo_np = find_faces(photo)

            for face in faces:
                sample = photo.subsurface(recognition.dlib2sdl(face).inflate((150,150)))
                sample = pygame.transform.scale(sample, (200,200))
                pygame.image.save(sample, os.path.join(imgdir, "thumbnails", str(thumbIndex) + ".png"))
                thumbIndex += 1

                index.write(img + "\t")
                index.write("\t".join(str(x) for x in recognition.getRepBBox(photo_np, face)))
                index.write("\n")

        except Exception, e:
            print "Failed to load:", imgpath, e
