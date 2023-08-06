import Image
from numpy import *
from OpenGL.GL import *
from zglUtils import *
from zglDrawer import *


# Static class for storing mouse information
#
class zglMouse(object):
    # Current and last buttons
    x = 0
    y = 0
    last_x = 0
    last_y = 0

    # Buttons
    left_button = 0
    middle_button = 0
    right_button = 0

    @staticmethod
    def setPosition(x, y):
        zglMouse.last_x = zglMouse.x
        zglMouse.last_y = zglMouse.y
        zglMouse.x = x
        zglMouse.y = y

    @staticmethod
    def mouseFunc(button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                zglMouse.left_button = 1
            elif state == GLUT_UP:
                zglMouse.left_button = 0
        if button == GLUT_RIGHT_BUTTON:
            if state == GLUT_DOWN:
                zglMouse.right_button = 1
            elif state == GLUT_UP:
                zglMouse.right_button = 0
        if button == GLUT_MIDDLE_BUTTON:
            if state == GLUT_DOWN:
                zglMouse.middle_button = 1
            else:
                zglMouse.middle_button = 0

    @staticmethod
    def getDelta():
        return (zglMouse.x - zglMouse.last_x, zglMouse.y - zglMouse.last_y)

# general zglObject
#
class zglObject(object):
    def __init__(self):
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        
        # If a quaternion is set, use it instead of self.rotation for the rotation
        self.quaternion = None		
        self.size = [1.0, 1.0, 1.0]
        self.colour = [1.0, 1.0, 1.0, 1.0]
        self.alpha = 1.0

        # Display list support
        self.useDisplayList = True
        self.displayList = -1

        # I wanted to use numpy for the array stuff but 
        # for some reason it seems a little bit slower
#		self.position = array([0, 0, 0])
#		self.rotation = array([0, 0, 0])
#		self.quaternion = None		# If a quaternion is set, use it instead of self.rotation for the rotation
#		self.size = array([1.0, 1.0, 1.0])
#		self.colour = array([1.0, 1.0, 1.0, 1.0])
#		self.alpha = 1.0

    # This function is defined because objects with multiple children objects
    # should inherit the parent's alpha. This function facilitates that ...
    # thus all zglObjects should have one even a trivial one to not cause errors
    def setAlpha(self, alpha):
        self.alpha = alpha

    def useColour(self, colour):
        if colour is not None:
            glColor4f(colour[0], colour[1], colour[2], colour[3])
            
    def useColourWithAlpha(self, colour, alpha):
        if colour is not None:
            glColor4f(colour[0], colour[1], colour[2], colour[3]*alpha)

    def doTranslation(self):
        glTranslate(self.position[0], self.position[1], self.position[2])

    def predraw(self):
        glPushMatrix()
        glTranslate(self.position[0], self.position[1], self.position[2])
        if self.quaternion is not None:
#			x, y, z, r = self.quaternion.XYZR()
#			glRotate(r*3.1415, x, y, z)
            glMultMatrixf( self.quaternion.glMatrix() )
        else:
            glRotate(self.rotation[0], 1, 0, 0)
            glRotate(self.rotation[1], 0, 1, 0)
            glRotate(self.rotation[2], 0, 0, 1)
            pass

        #glColor4f(self.colour[0], self.colour[1], self.colour[2], self.colour[3]*self.alpha)
        self.useColourWithAlpha(self.colour, self.alpha)

        return

    def postdraw(self):
        glPopMatrix()

    def maindraw(self):
        # This is where the main GL draw code goes
        pass

    def draw(self):

        if not self.visible():
            return
        
        self.predraw()

        if glIsList(self.displayList):
            glCallList(self.displayList)
        else:
            if self.useDisplayList:
                self.displayList = glGenLists(1)

                glNewList(self.displayList, GL_COMPILE_AND_EXECUTE)
                self.maindraw()
                glEndList()
            else:
                self.maindraw()

        self.postdraw()
        return


    # Return the radius of the sphere that bounds this object
    # subclasses will have to override this if self.size it
    # not accurate
    #
    def getBoundingRadius(self):
        return max(self.size)

    def visible(self, value=None):
        if value is not None:
            self._visible = value
        if not hasattr(self, '_visible'):
            self._visible = True
        return self._visible
    
    # END class zglObject
    pass


class zglLine(zglObject):

    def __init__(self):
        zglObject.__init__(self)
        self.points = []

    def maindraw(self):
        if len(self.points) < 2:
            return
        self.useColour(self.colour)
        zglDrawer.drawLine(self.points)
        return

    # END class zglLine
    pass



class zglRect(zglObject):
    
    def __init__(self):
        zglObject.__init__(self)
        self.borderColour = None
        
        # whether or not to use position as bottom-left corner of rect
        self.corner_mode = False
        
        self.use_texture = False
        return


    def setTexture(self, texture_id, texture_coords):
        self.texture_id = texture_id
        self.texture_coords = texture_coords
        self.use_texture = True

    def setTextureImage(self, image, mode='RGBX'):
        ix = image.size[0]
        iy = image.size[1]
        image = image.tostring("raw", mode, 0, -1)

        # Create Texture
        new_texture_id = glGenTextures(1)
        self.texture_id = new_texture_id
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        self.texture_coords = ( (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0) )
        self.use_texture = True

    def setTextureImageFile(self, texture_image_file, mode='RGBX'):
        image = Image.open(texture_image_file)
        self.setTextureImage(image, mode=mode)
        self.texture_coords = ( (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0) )
        # self.texture_id = zglUtils.loadTextureImage(texture_image_file)
        self._texture_image_file = texture_image_file
        return


    def maindraw(self):
        if not self.corner_mode:
            glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)

        if self.use_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glBegin(GL_QUADS);
            glNormal3f(0.0, 0.0, 1.0);
            glTexCoord2f(self.texture_coords[0][0], self.texture_coords[0][1])
            glVertex2f(0, 0)
            glTexCoord2f(self.texture_coords[1][0], self.texture_coords[1][1])
            glVertex2f(self.size[0], 0)
            glTexCoord2f(self.texture_coords[2][0], self.texture_coords[2][1])
            glVertex2f(self.size[0], self.size[1])
            glTexCoord2f(self.texture_coords[3][0], self.texture_coords[3][1])
            glVertex2f(0, self.size[1])
            glEnd()
            glDisable(GL_TEXTURE_2D)

        elif self.colour is not None:
            glBegin (GL_QUADS);
            glNormal3f(0.0, 0.0, 1.0);
            glVertex2f(0, 0)
            glVertex2f(self.size[0], 0)
            glVertex2f(self.size[0], self.size[1])
            glVertex2f(0, self.size[1])
            glEnd ()

        if self.borderColour is not None:
            self.useColour(self.borderColour)
            glBegin (GL_LINE_LOOP)
            glVertex2f(0, 0)
            glVertex2f(self.size[0], 0)
            glVertex2f(self.size[0], self.size[1])
            glVertex2f(0, self.size[1])
            glEnd ()

        return

    def drawStroke(self):
        self.predraw()
        if not self.corner_mode:
            glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)
        glBegin (GL_LINE_LOOP)
        glVertex2f(0, 0)
        glVertex2f(self.size[0], 0)
        glVertex2f(self.size[0], self.size[1])
        glVertex2f(0, self.size[1])
        glEnd ()
        self.postdraw()

    def getBoundingRadius(self):
        return SQRT_2 * max(self.size)

    # END class zglRect
    pass



class zglEllipse(zglObject):
    def __init__(self):
        zglObject.__init__(self)
        self.borderColour = None
        self.corner_mode = False	# whether or not to use position as bottom-left corner of rect

    def maindraw(self):
        
        if not self.corner_mode:
            glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)

        # we want at least 8 wedges
        # and for now, a max 
        smoothness = max(8, self.size[0])
        smoothness = min(smoothness, 360)
        
        x = self.size[0]/2.0
        y = self.size[1]/2.0
        
        # TODO:
        # radius is only for circle
        # need to calculate for an actual ellipse
        radius = self.size[0]/2.0
            
        if self.colour is not None:
            
            glBegin(GL_TRIANGLE_FAN)
            glNormal3f(0.0, 0.0, 1.0);
            for i in range(0, smoothness):    
                angle = i * math.pi * 2.0 / smoothness
                glVertex2f(x + radius * math.cos(angle), 
                           y + radius * math.sin(angle))
            glEnd() 

            
        if self.borderColour is not None:
            self.useColour(self.borderColour)
            
            glBegin(GL_LINE_LOOP)
            for i in range(0, smoothness):    
                angle = i * math.pi * 2.0 / smoothness
                glVertex2f(x + radius * math.cos(angle), 
                           y + radius * math.sin(angle))
            glEnd() 

        return
            
    def drawStroke(self):
        self.predraw()
        if not self.corner_mode:
            glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)
        glBegin (GL_LINE_LOOP)
        glVertex2f(0, 0)
        glVertex2f(self.size[0], 0)
        glVertex2f(self.size[0], self.size[1])
        glVertex2f(0, self.size[1])
        glEnd ()
        self.postdraw()
        return

    # END class zglEllipse
    pass


class zglTriangle(zglObject):
    def __init__(self):
        zglObject.__init__(self)
        self.borderColour = None
        self.corner_mode = False	# whether or not to use position as bottom-left corner of rect
        return
    
    
    def maindraw(self):
        
        if not self.corner_mode:
            glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)

        # we want at least 8 wedges
        # and for now, a max 
        smoothness = max(8, self.size[0])
        smoothness = min(smoothness, 360)
        
        x = self.size[0]/2.0
        y = self.size[1]/2.0
        
        # TODO:
        # radius is only for circle
        # need to calculate for an actual ellipse
        radius = self.size[0]/2.0
            
        if self.colour is not None:
            
            glBegin (GL_QUADS);
            glNormal3f(0.0, 0.0, 1.0);
            glVertex2f(0, 0)
            glVertex2f(self.size[0], 0)
            glVertex2f(self.size[0]/2, self.size[1])
            glEnd ()
            
            
        if self.borderColour is not None:
            self.useColour(self.borderColour)

            
            glBegin (GL_LINE_LOOP)
            glVertex2f(0, 0)
            glVertex2f(self.size[0], 0)
            glVertex2f(self.size[0]/2, self.size[1])
            glEnd ()

        return
            

    # END class Triangle
    pass




