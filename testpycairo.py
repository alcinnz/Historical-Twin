#!/usr/bin/env python
import cairo
import pygame
import math

size = 400, 400

# Initialize pygame with 32-bit colors. This setting stores the pixels
# in the format 0x00rrggbb.
pygame.init()
screen = pygame.display.set_mode(size, 0, 32)

# Get a reference to the memory block storing the pixel data.
pixels = pygame.surfarray.pixels2d(screen)

# Set up a Cairo surface using the same memory block and the same pixel
# format (Cairo's RGB24 format means that the pixels are stored as
# 0x00rrggbb; i.e. only 24 bits are used and the upper 16 are 0).
cairo_surface = cairo.ImageSurface.create_for_data(
	pixels.data, cairo.FORMAT_RGB24, size[0], size[1])

# Draw a smaller black circle to the screen using Cairo.
cr = context = cairo.Context(cairo_surface)

cr.set_source_rgb(1,1,1)
        
cr.select_font_face("futura", cairo.FONT_SLANT_NORMAL, 
    cairo.FONT_WEIGHT_BOLD)
cr.set_font_size(30)

cr.move_to(20, 30)
cr.text_path("FIND YOUR TWIN")

cr.stroke_preserve()
cr.set_source_rgb(0.5, 0.5, 0.5)
cr.fill()

# Flip the changes into view.
pygame.display.flip()

# Wait for the user to quit.
while pygame.QUIT not in [e.type for e in pygame.event.get()]:
	pass
