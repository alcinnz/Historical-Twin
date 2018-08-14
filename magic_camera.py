#! /usr/bin/python2
import magic_mirror as mirror
from pygame import event, transform, QUIT, KEYDOWN, MOUSEBUTTONUP
import pygame, os.path
from recognition import getRepBBox, average, l2_dist, dlib2sdl

captions = {}
with open("creditlines.tsv") as f:
    f.readline() # Skip headers
    for line in f:
        id_, caption = line.strip().split("\t")
        captions[id_] = caption

# Common utilities
def centerx(img, y = "mid"):
    if y == "mid":
        y = mirror.screen.get_height()/2 - img.get_height()/2
    pos = mirror.screen.get_width()/2 - img.get_width()/2, y
    mirror.screen.blit(img, pos)

def video(msg = "", font_size = 40):
    fill((0,0,0))
    capture = transform.flip(mirror.camera.get_image(), True, False)
    centerx(scaley(capture, fix=True), 0)

def frame():
    pygame.display.flip()
    mirror.clock.tick(60)

    evts = [evt.type for evt in event.get()]
    if QUIT in evts or KEYDOWN in evts:
        pygame.quit()
        exit()
    return MOUSEBUTTONUP not in evts

def fill(colour = (255,255,255)):
    s = mirror.screen
    fullscreen = pygame.Rect(0, 0, s.get_width(), s.get_height())
    pygame.draw.rect(s, colour, fullscreen)

def flash():
    fill()
    pygame.display.flip()

    yield None

    mirror.clock.tick(9)

def scaley(img, height=mirror.screen.get_height(), fix = False):
    if not fix and img.get_height() <= height: return img

    _width, _height = float(img.get_width()), float(img.get_height())
    size = int(_width * (height/_height)), int(height)
    return pygame.transform.smoothscale(img, size)

# States
startbutton = pygame.image.load("assets/BU_touchToBegin.png")
startbutton = pygame.transform.scale(startbutton, (300,300))
start_message = pygame.image.load("assets/intro_text.png")
def intro():
    import random

    s = mirror.screen
    while True:
        fill((100,100,100))

        samples = []
        for x in range(0, s.get_width(), 200):
            for y in range(0, s.get_height(), 200):
                if not samples:
                    samples = list(mirror.photo_samples) # Clone
                    random.shuffle(samples)
                s.blit(samples.pop(), (x,y))

        centerx(start_message, 50)

        centerx(startbutton, s.get_height() - startbutton.get_height() - 20)
        while frame(): pass
        terms()

capture_button = pygame.image.load("assets/BU_takePhoto.png")
capture_button = pygame.transform.scale(capture_button, (300,300))
intro_message = scaley(pygame.image.load("assets/intro_bkgd.jpg"))
def terms():
    fill()

    def center_y(img):
        return mirror.screen.get_height()/2 - img.get_height()/2
    mirror.screen.blit(intro_message, (20, center_y(intro_message)))

    pos = mirror.screen.get_width() - capture_button.get_width() - 80, center_y(capture_button)
    mirror.screen.blit(capture_button, pos)

    while frame(): pass
    capture()

countdown = [scaley(pygame.image.load("assets/UI_countdown_%i.png" % i), 300)
        for i in range(3, 0, -1)]
def capture():
    for i in range(3):
        for j in range(60):
            if not frame(): return
            video()
            centerx(countdown[i])

    find_faces()
take_photo = capture

def find_faces():
    faces, face = [], None
    capture = pygame.transform.flip(scaley(mirror.camera.get_image(), fix=True), True, False)
    for _ in flash():
        faces, capture_np = mirror.find_faces(capture)
        if len(faces) == 1: face = getRepBBox(capture_np, faces[0])

    if len(faces) == 0:
        centerx(mirror.write("NO FACE RECOGNIZED", (255,0,0)))
        for i in range(10*60):
            if not frame(): return
    elif face is None:
        select_face(capture, capture_np, faces)
    else: match(face, faces[0], capture)

select_msg = pygame.image.load("assets/UI_selectFaceTxt.png")
if select_msg.get_width() > mirror.screen.get_width():
    size = mirror.screen.get_width(), select_msg.get_height()
    select_msg = pygame.transform.smoothscale(select_msg, size)
def select_face(capture, capture_np, faces):
    fill((0,0,0))
    out = capture.copy()
    for face in faces: pygame.draw.rect(out, mirror.font_colour, dlib2sdl(face), 2)

    mirror.screen.blit(out, (0,0))

    centerx(select_msg, 50)

    retake_pos = mirror.screen.get_width() - newtake.get_width(), mirror.screen.get_height() - newtake.get_height()
    mirror.screen.blit(newtake, retake_pos)

    for i in range(180*60):
        if frame(): continue

        hit = None
        cursor = pygame.mouse.get_pos()
        if cursor[0] > retake_pos[0] and cursor[1] > retake_pos[1]:
            return take_photo()
        for face in faces:
            if dlib2sdl(face).collidepoint(cursor):
                hit = face
        if hit is not None:
            face = None
            for _ in flash(): face = getRepBBox(capture_np, hit)
            match(face, hit, capture)
        return

def score(face1, face2):
    d = l2_dist(face1, face2)
    if d <= 1:
        return 80 + (1 - d) * 20
    elif d <= 1.5:
        d = (1.5 - d)/0.5
        return 20 + d * 60
    elif d <= 3:
        d = (3 - d)/1.5
        return d * 20
    else:
        return 0

def crop(img, x, y, width, height):
    if x + width > img.get_width(): width = img.get_width() - x
    if y + height > img.get_height(): width = img.get_height() - y
    return img.subsurface(pygame.Rect(x, y, width, height))

def crop_webcam(photo, face_bbox, crop_width = mirror.screen.get_width()/2 - 10):
    old_width = photo.get_width()
    photo = scaley(photo, fix = True)
    scale_width = float(photo.get_width())/old_width

    if crop_width >= photo.get_width(): return photo
    midx = int(dlib2sdl(face_bbox).centerx * scale_width)
    cropx = max(midx - crop_width/2, 0)

    return crop(photo, cropx, 0, crop_width, photo.get_height())

newtake = pygame.image.load("assets/BU_takeNewPhoto.png")
newtake = pygame.transform.smoothscale(newtake, (200, 200))
match_bg = pygame.image.load("assets/UI_match_bkgd.png")
match_bg = pygame.transform.smoothscale(match_bg, (250, 250))
def match(face, facebbox, thumbnail):
    match, path = mirror.index.nearest_keyed(face)
    photo = scaley(pygame.image.load(path))

    # Background
    s = mirror.screen
    fullscreen = pygame.Rect(0, 0, s.get_width(), s.get_height())
    pygame.draw.rect(s, mirror.font_colour, fullscreen)

    # Thumbnail display
    print thumbnail
    if thumbnail:
        thumbnail = crop_webcam(thumbnail, facebbox, photo.get_width())
        pos = (s.get_width() - thumbnail.get_width(), s.get_height()/2 - thumbnail.get_height()/2)
        mirror.screen.blit(thumbnail, pos)

    # Photo display
    photo = scaley(photo)
    mirror.screen.blit(scaley(photo), (0,0))

    # caption
    caption = captions.get(os.path.basename(path)[:-4])
    if not caption: caption = os.path.basename(path)[:-4]
    width, height = mirror.font(30).size(caption)
    x, y = pos = s.get_width()/4 - width/2, s.get_height() - height
    pygame.draw.rect(s, (0,0,0), pygame.Rect(max(x, 0), y, width, height))
    s.blit(mirror.write(caption, (255,255,255), 30), (max(x, 0), y))

    centerx(match_bg, "mid")
    centerx(mirror.write("%i%%" % score(match, face), font_size = 80),
            mirror.screen.get_height()/2 - 80)

    centerx(newtake, mirror.screen.get_height() - newtake.get_height() - 40)
    # display!
    pygame.display.flip()
    for i in range(180*60):
        if not frame(): return

if __name__ == "__main__": intro()
