#!/usr/bin/python

import os
import sys

APP_ROOT = os.getenv('ZGL_HOME')
sys.path.insert(0, '%s/src' % APP_ROOT)

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from zgl.zglText import *

font = None
width = 600
height = 600

def do_ortho():
    w, h = width, height
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    size = max(w, h) / 2.0
    aspect = float(w) / float(h)
    if w <= h:
        aspect = float(h) / float(w)
        glOrtho(-size, size, -size*aspect, size*aspect, -100000.0, 100000.0)
    else:
        glOrtho(-size*aspect, size*aspect, -size, size, -100000.0, 100000.0)
    glScaled(aspect, aspect, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_scene():
    
    glColor3f(1.0, 1.0, 1.0)
    
    text = ["Hello", "This is a test", "Of zglText using FTGL"]
    for i in range(len(text)):
        line = text[i]
        text1 = font.draw(line);
        glTranslatef(0.0, - font.getSize(line)[1] - 5, 0.0)
            
  
def on_display():
    glClear(GL_COLOR_BUFFER_BIT)
    do_ortho()
    draw_scene()
    glutSwapBuffers()

def on_reshape(w, h):
    width, height = w, h

def on_key(key, x, y):
    if key == '\x1b':
        sys.exit(1)

if __name__ == '__main__':
    glutInitWindowSize(width, height)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE)
    glutCreateWindow("zglText FTGL Test")
    glClearColor(0.0, 0.0, 0.0, 0.0)

    try:
        font = zglFTGLFont(sys.argv[1], 24)
    except:
        print "usage:", sys.argv[0], "font_filename.ttf"
        sys.exit(0)

    glutDisplayFunc(on_display)
    glutReshapeFunc(on_reshape)
    glutKeyboardUpFunc(on_key)

    glutMainLoop()
