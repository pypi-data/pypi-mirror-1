from pymt import *
import collections
import os
import sys
import pygame
import random

# search images
q = collections.deque()
max = 200
for root, dirs, files in os.walk(sys.argv[0]):
    for filename in files:
        if max < 0:
            break
        ext = filename.split('.')[-1].lower()
        if ext not in ('png', 'jpg', 'jpeg'):
            continue
        q.append(os.path.join(root, filename))
        max -= 1

plane = MTScatterPlane()

def _image_loaded(image, scatter):
    scatter.scale = 1 / (image.width / 320.)

def _image_resize(image):
    if image.width > 640 or image.height > 480:
        data = image._data
        im = pygame.image.fromstring(data.data, (data.width, data.height), data.mode)
        im = pygame.transform.scale(im, (640, 480))
        data = ImageData(im.get_width(), im.get_height(),
                         data.mode,
                         pygame.image.tostring(im, data.mode, True))
        image._data = data
    return image

# deque
def _delayed_deque(*largs):
    for x in xrange(2):
        try:
            filename = q.pop()
        except:
            return

        pos = map(lambda x: random.random() * x, getWindow().size)
        rotation = random.random() * 360
        img = Loader.image(filename, tcallback=_image_resize)
        m = MTScatterImage(image=img, pos=pos, rotation=rotation)
        plane.add_widget(m)

        img.connect('on_load', curry(_image_loaded, img, m))

getClock().schedule_interval(_delayed_deque, 1 / 25.)

runTouchApp(plane)
