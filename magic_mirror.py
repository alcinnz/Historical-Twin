#! /usr/bin/python2
import time
start = time.time()

import pygame, numpy
import pygame.camera

# Init display
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption("Magic Mirror")

#pygame.mouse.set_visible(False)

# Init font
pygame.font.init()
font_colour = 16, 117, 186
fonts = {40: pygame.font.Font("Futura.ttc", 40)}
def font(font_size = 40):
    if font_size not in fonts:
        fonts[font_size] = pygame.font.Font("Futura.ttc", font_size)
    return fonts[font_size]

def write(text, colour = font_colour, font_size = 40):
    return font(font_size).render(str(text), True, colour)

# Init AI
import recognition
import sys, os

def find_faces(pygame_capture):
    capture = numpy.array(pygame.surfarray.pixels3d(pygame_capture))
    capture = numpy.swapaxes(capture, 0, 1)
    return recognition.align.getAllFaceBoundingBoxes(capture), capture

index = recognition.MultiBinaryTree()
imgdir = sys.argv[1] if len(sys.argv) > 1 else "images"
photo_samples = []

screen.blit(write("Loading index... %fs" % (time.time() - start)), (0,0))
pygame.display.flip()
with open(os.path.join(imgdir, "index.tsv")) as f:
    for line in f:
        line = line.strip().split("\t")
        img = os.path.join(imgdir, line[0])
        description = numpy.array([float(n) for n in line[1:]])
        index.insert(description, img)

screen.blit(write("Loading images... %fs" % (time.time() - start)), (0,50))
pygame.display.flip()
for img in os.listdir(os.path.join(imgdir, "thumbnails")):
    photo_samples.append(pygame.image.load(os.path.join(imgdir, "thumbnails", img)))

# Init clock
clock = pygame.time.Clock()

# Init camera
pygame.camera.init()

cameras = pygame.camera.list_cameras()
if not cameras:
    pygame.quit()
    print "No cameras found, exiting!"
    sys.exit(1)
camera = pygame.camera.Camera(cameras[0])

camera.start()

# Mainloop
def recognize(capture, faces):
    fullscreen = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
    pygame.draw.rect(screen, (255, 255, 255), fullscreen)
    pygame.display.flip()

    face = recognition.average(recognition.getRepBBox(capture, face) for face in faces)

    img = index.nearest(face)
    screen.blit(pygame.image.load(img), (0,0))
    pygame.display.flip()
    pygame.time.wait(10*1000) # 30s

def main():
    countdown = 10
    lastFaceCount = 0
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                return

        capture = camera.get_image()
        faces, capture_data = find_faces(capture)
        for bbox in faces:
            rect = pygame.Rect(bbox.left(), bbox.top(), bbox.width(), bbox.height())
            pygame.draw.rect(capture, (255, 0, 0), rect, 2)

        capture = pygame.transform.flip(capture, True, False)
        screen.blit(pygame.transform.smoothscale(capture, screen.get_size()), (0,0))

        if len(faces) == 0 or len(faces) != lastFaceCount:
            countdown = 10
            lastFaceCount = len(faces)
        elif countdown == 0:
            recognize(capture_data, faces)
            countdown = 10
        else:
            screen.blit(write(countdown), (0,0))
            countdown -= 1

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
