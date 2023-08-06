#! /usr/bin/env python
'''Attempt to get a depth-texture-based shadow demo
'''
import OpenGL 
#OpenGL.USE_ACCELERATE = False
OpenGL.FULL_LOGGING = True
from OpenGLContext import testingcontext
BaseContext, MainFunction = testingcontext.getInteractive()
from OpenGLContext.scenegraph.basenodes import *
from OpenGL.GL import *
from OpenGLContext.arrays import array, frombuffer
from OpenGL.arrays import vbo
import string, time
import ctypes,weakref

LIGHT_VERT = """
	void main() {
		gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	}"""
LIGHT_FRAG = """
	void main() {
		gl_FragColor = vec4( 0,0,0,0 );
	}"""




class TestContext( BaseContext ):
	currentImage = 0
	currentSize = 0
	lightTexture = None
	lightTransform = None
	def Render( self, mode = 0):
		BaseContext.Render( self, mode )
		
		
		
		self.shape.Render( mode )
		width,height = self.getViewPort()
		self.vbo.bind()
		glReadPixels(
			0, 0, 
			300, 300, 
			GL_RGBA, 
			GL_UNSIGNED_BYTE,
			self.vbo,
		)
		# map_buffer returns an Byte view, we want an 
		# UInt view of that same data...
		data = map_buffer( self.vbo ).view( 'I' )
		print data
		del data
		self.vbo.unbind()
		
	def OnInit( self ):
		"""Scene set up and initial processing"""
		self.vbo = vbo.VBO( 
			None,
			target = GL_PIXEL_PACK_BUFFER,
			usage = GL_DYNAMIC_READ,
			size = 300*300*4,
		)
		self.shape = Shape(
			geometry = Teapot( size=2.5 ),
			appearance = Appearance(
				material = Material(
					diffuseColor =(1,1,1)
				),
				texture = ImageTexture(
					url = ["nehe_wall.bmp"]
				),
			),
		)

if __name__ == "__main__":
	MainFunction ( TestContext)

