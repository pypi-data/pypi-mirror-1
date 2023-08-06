#! /usr/bin/env python
'''=Point-light Shadows=

[shadow_3.py-screen-0001.png Screenshot]

In this tutorial, we will:

    * subclass our previous shadow tutorial code 
    * render our shadows to cube-maps to support point light sources 

Again, this is a fairly minor change to our previous 
tutorial code.
'''
import OpenGL,sys,os,traceback
from shadow_2 import TestContext as BaseContext
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.depth_texture import *
from OpenGL.GL.ARB.shadow import *
from OpenGL.GL.ARB.texture_cube_map import *
from OpenGL.GL.framebufferobjects import *
from OpenGLContext.scenegraph.basenodes import *
from OpenGLContext.arrays import pi

class TestContext( BaseContext ):
    """Shadow rendering tutorial code"""
    def createLights( self ):
        """Create the light's we're going to use to cast shadows"""
        return [
            SpotLight(
                location = [0,5,10],
                color = [1,.95,.95],
                intensity = .5,
                ambientIntensity = 0.10,
                direction = [0,-5,-10],
            ),
            PointLight( 
                location = [2,.5,0],
                color = [.95,1,1],
                intensity = .5,
                ambientIntensity = .10
            ),
        ]
    textureTargetMap = {
        "": GL_TEXTURE_2D,
        "pos_x": GL_TEXTURE_CUBE_MAP_POSITIVE_X_ARB,
        "pos_y": GL_TEXTURE_CUBE_MAP_POSITIVE_Y_ARB,
        "pos_z": GL_TEXTURE_CUBE_MAP_POSITIVE_Z_ARB,
        "neg_x": GL_TEXTURE_CUBE_MAP_NEGATIVE_X_ARB,
        "neg_y": GL_TEXTURE_CUBE_MAP_NEGATIVE_Y_ARB,
        "neg_z": GL_TEXTURE_CUBE_MAP_NEGATIVE_Z_ARB,
    }
    cubeDirectionMap = {
        "pos_x": (1,0,0),
        "pos_y": (0,1,0),
        "pos_z": (0,0,1),
        "neg_x": (-1,0,0),
        "neg_y": (0,-1,0),
        "neg_z": (0,0,-1),
    }
    
    cubeShadowSize = 256
    
    def renderLightTexture( self, light, mode, direction=None, fov=pi/3.0, textureKey="" ):
        """Create 6 cube-mapped textures for each point-light"""
        if isinstance( light, SpotLight ):
            return super(TestContext,self).renderLightTexture(
                light, mode, direction, fov, textureKey 
            )
        
        # Okay, what do we need to do for a cube-map instead?
        shadowMapSize = self.cubeShadowSize
        token = mode.cache.getData(light,key=self.textureCacheKey)
        cubeTarget = GL_TEXTURE_CUBE_MAP_ARB
        if not token:
            fbo = glGenFramebuffers(1)
            '''It has to be bound to configure it.'''
            glBindFramebuffer(GL_FRAMEBUFFER, fbo )
            '''The texture itself is the same as the last tutorial.'''
            texture = glGenTextures( 1 )
            
            glBindTexture( cubeTarget, texture )
            for key,dir in self.cubeDirectionMap.items():
                target = self.textureTargetMap[ key ]
                glTexImage2D( 
                    target, 
                    0, 
                    GL_DEPTH_COMPONENT, 
                    shadowMapSize, shadowMapSize, 0,
                    GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE, None
                )
            holder = mode.cache.holder( 
                light,(fbo,texture),key=self.textureCacheKey
            )
        else:
            fbo,texture = token 
            glBindFramebuffer(GL_FRAMEBUFFER, fbo )
            '''Make the texture current to configure parameters.'''
            glBindTexture( cubeTarget, texture )
        for key,dir in self.cubeDirectionMap.items():
            tex,matrix = super( TestContext, self ).renderLightTexture(
                light, mode, dir, fov = pi/2, textureKey = key,
            )
            
            
    def setupShadowContext( self, light=None, mode=None, textureKey="" ):
        """Create a shadow-rendering context/texture"""
        if isinstance( light, SpotLight ):
            return super(TestContext,self).setupShadowContext(
                light, mode, textureKey 
            )
        shadowMapSize = self.cubeShadowSize
        glViewport(0,0,shadowMapSize,shadowMapSize)
        fbo,tex = mode.cache.getData(light,key=self.textureCacheKey)
        # okay, so we're a point-light and need to do setup for our light...
        target = self.textureTargetMap[ textureKey ]
        cubeTarget = GL_TEXTURE_CUBE_MAP_ARB
        glTexParameteri(cubeTarget, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(cubeTarget, GL_TEXTURE_MAG_FILTER, self.FILTER_TYPE)
        glTexParameteri(cubeTarget, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(cubeTarget, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, 
            GL_DEPTH_ATTACHMENT, 
            target, 
            tex, 
            0 #mip-map level...
        )
        glDrawBuffer( GL_NONE )
        try:
            checkFramebufferStatus( )
        except Exception, err:
            traceback.print_exc()
            import os
            os._exit(1)
        glBindTexture( cubeTarget, 0 )
        glClear(GL_DEPTH_BUFFER_BIT)
        return tex, 

if __name__ == "__main__":
    TestContext.ContextMainLoop(
        depthBuffer = 24,
    )
