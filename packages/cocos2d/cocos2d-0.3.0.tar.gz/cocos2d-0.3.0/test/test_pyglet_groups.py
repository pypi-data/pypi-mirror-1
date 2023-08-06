import pyglet
from pyglet.gl import *

window = pyglet.window.Window()

grossini = pyglet.resource.image("grossini.png")
grossini.anchor_x = grossini.width / 2
grossini.anchor_y = grossini.height / 2

class MySpriteGroup(pyglet.graphics.Group):
    def __init__(self, sprite):
        super(MySpriteGroup, self).__init__(parent=sprite.group)
        self.sprite = sprite
        
    def set_state(self):
        glPushMatrix()
        self.transform()
        
    def unset_state(self):
        glPopMatrix()
        
    def transform( self ):
        """Apply ModelView transformations"""
        if self.sprite.position != (0,0):
            glTranslatef( self.sprite.position[0], self.sprite.position[1], 0 )

        if self.sprite.scale != 1.0:
            glScalef( self.sprite.scale, self.sprite.scale, 1)

        if self.sprite.rotation != 0.0:
            glRotatef( -self.sprite.rotation, 0, 0, 1)
            
            
batch = pyglet.graphics.Batch()
s1 = pyglet.sprite.Sprite( grossini )
s1.batch = batch
s1.position=(320,100)
g1 = MySpriteGroup(s1)

s2 = pyglet.sprite.Sprite( grossini )
s2.batch = batch
s2.group = g1

s2.position=(00,100)
g2 = MySpriteGroup(s2)
s3 = pyglet.sprite.Sprite( grossini )
s3.batch = batch
s3.group = g2

s3.position=(00,100)


def update(dt):
    s1.rotation += 360*dt
    s2.rotation += 360*dt
    s3.rotation += 360*dt
pyglet.clock.schedule_interval(update, 1/60.)

@window.event
def on_draw():
    window.clear()
    batch.draw()
    
pyglet.app.run()