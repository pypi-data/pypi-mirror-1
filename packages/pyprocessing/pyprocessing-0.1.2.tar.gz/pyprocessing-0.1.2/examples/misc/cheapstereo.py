from pyprocessing import *

def setup():
  """Initialization and setup."""
  # window setup
  size(200, 100, resizable=True)
  # Illumination setup
  lights()
  
def scene():
  """Draws a simple scene."""
  glPushMatrix ()
  glRotatef (60, 0, 1, 0)
  box(45)
  glPopMatrix()
  
def draw():
  """Display callback."""
  # Projection setup
  glMatrixMode (GL_PROJECTION)
  glLoadIdentity()
  gluPerspective (60,width*0.5/height, 1, 200)
  # clear screen
  background (200)
  # First camera
  glViewport (0,0,width/2,height)
  glMatrixMode (GL_MODELVIEW)
  glLoadIdentity()
  gluLookAt (-2, 10, 100, 0, 0, 0, 0, 1, 0)
  scene()
  # Second camera  
  glViewport (width/2,0,width/2,height)
  glMatrixMode (GL_MODELVIEW)
  glLoadIdentity()
  gluLookAt (2, 10, 100, 0, 0, 0, 0, 1, 0)
  scene()
  
run()
