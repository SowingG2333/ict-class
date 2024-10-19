"""
Inferemote: a Remote Inference Toolkit for Ascend 310

Base on code from https://gitee.com/ascend/samples.git
Copyright (c) 2021 Jiasheng Hao <haojiash@qq.com>
(University of Electronic Science and Technology of China, UESTC)

Permission  is  hereby  granted,  free  of  charge,  to  any  person
obtaining a copy of this software and associated documentation files
(the  "Software"),  to deal  in  the  Software without  restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to  permit persons to whom  the Software is furnished  to do so,
subject to the following conditions:

The  above copyright  notice  and this  permission  notice shall  be
included in all copies or substantial portions of the Software.

THE  SOFTWARE IS  PROVIDED "AS  IS", WITHOUT  WARRANTY OF  ANY KIND,
EXPRESS OR IMPLIED,  INCLUDING BUT NOT LIMITED TO  THE WARRANTIES OF
MERCHANTABILITY,    FITNESS   FOR    A   PARTICULAR    PURPOSE   AND
NONINFRINGEMENT. IN NO EVENT SHALL  THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR  ANY CLAIM, DAMAGES OR OTHER LIABILITY,  WHETHER IN AN
ACTION OF  CONTRACT, TORT OR OTHERWISE,  ARISING FROM, OUT OF  OR IN
CONNECTION WITH  THE SOFTWARE OR  THE USE  OR OTHER DEALINGS  IN THE
SOFTWARE.

"""
import sys, os
import numpy as np
import cv2 as cv

from inferemote.atlas_remote import AtlasRemote
from inferemote.image_encoder import ImageEncoder

class Picasso(AtlasRemote):
    MODEL_WIDTH  = 1080
    MODEL_HEIGHT = 720

    def __init__(self, **kwargs):
        super().__init__(port=5552, **kwargs)

    def pre_process(self, bgr_img):
        rgb_img = cv.cvtColor(bgr_img, cv.COLOR_BGR2RGB)
        rgb_img = cv.resize(rgb_img, (self.MODEL_WIDTH, self.MODEL_HEIGHT))
        '''NO transposing here! jpeg encoding of the bytes will not apply by opencv.'''
        #rgb_img = rgb_img.transpose(2, 0, 1).copy()
        ''' Encode to bytes before push to remote models'''
        blob = ImageEncoder.image_to_bytes(rgb_img)

        return blob

    def post_process(self, result):
        result = result[0]

        ''' Decode to image after net travelling '''
        image = ImageEncoder.bytes_to_image(result)
        # print(image.shape)

        '''NO transposing here! jpeg encoding of the bytes will not apply by opencv.'''
        #result = result.reshape(3, 360, 540).astype(np.float32)
        #res_blob = result.transpose(1, 2, 0).copy()

        ''' set type to uint8 for VideoWriter '''
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR).astype(np.uint8)

        return image

''' Ends. '''
