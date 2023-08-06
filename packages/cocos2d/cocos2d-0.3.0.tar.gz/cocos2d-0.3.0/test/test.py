# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cocos
from cocos.sprite import Sprite
from cocos.actions import *

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        sprite1 = Sprite('grossini.png')
        sprite2 = Sprite('grossinis_sister1.png')

        sprite1.add(sprite2)
        self.add(sprite1)
        sprite1.position = (320,240)
        #print sprite1.anchor
        print sprite1.transform_anchor
        print sprite1.children_anchor
        print sprite2.transform_anchor
        print sprite2.children_anchor

if __name__ == '__main__':
    cocos.director.director.init()
    cocos.director.director.run(cocos.scene.Scene(TestLayer()))