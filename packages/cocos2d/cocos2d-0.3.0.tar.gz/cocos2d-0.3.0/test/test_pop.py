# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import ActionSprite
from cocos.actions import *
import pyglet
        
        

if __name__ == "__main__":
    director.init()
    test_layer = cocos.layer.ColorLayer(255,0,0,255)
    main_scene = cocos.scene.Scene (test_layer)
    test_layer.do( Delay(5) + CallFunc(director.pop) )
    director.run (main_scene)
