import numpy as np
import mxnet as mx
from mxnet import nd, init
from mxnet.gluon import nn
import mxnet.ndarray as F
from mxnet.gluon.nn import HybridBlock

from .. import dilatedresnet as resnet
from ..segbase import SegBaseModel

class FCN(SegBaseModel):
    r"""Fully Convolutional Networks for Semantic Segmentation

    Parameters
    ----------
    nclass : int
        Number of categories for the training dataset.
    backbone : string
        Pre-trained dilated backbone network type (default:'resnet50'; 'resnet50', 'resnet101' or 'resnet152').
    norm_layer : object
        Normalization layer used in backbone network (default: :class:`mxnet.gluon.nn.BatchNorm`;


    Reference:

        Long, Jonathan, Evan Shelhamer, and Trevor Darrell. "Fully convolutional networks for semantic segmentation." *CVPR*, 2015
    """
    def __init__(self, nclass, backbone='resnet50', norm_layer=nn.BatchNorm):
        super(FCN, self).__init__(backbone, norm_layer)
        with self.name_scope():
            self.head = FCNHead(nclass, norm_layer=norm_layer)
        self.head.initialize(init=init.Xavier())

    # def hybrid_forward(self, F, x):
    def forward(self, x):
        _, _, H, W = x.shape
        x = self.pretrained(x)
        x = self.head(x)
        x = F.contrib.BilinearResize2D(x, height=H, width=W)
        return x


class FCNHead(HybridBlock):
    def __init__(self, nclass, norm_layer):
        super(FCNHead, self).__init__()
        with self.name_scope():
            self.block = nn.HybridSequential(prefix='')
            self.block.add(norm_layer(in_channels=2048))
            self.block.add(nn.Activation('relu'))
            self.block.add(nn.Conv2D(in_channels=2048, channels=512,
                           kernel_size=3, padding=1))
            self.block.add(norm_layer(in_channels=512))
            self.block.add(nn.Activation('relu'))
            self.block.add(nn.Dropout(0.1))
            self.block.add(nn.Conv2D(in_channels=512, channels=nclass,
                           kernel_size=1))
    
    def hybrid_forward(self, F, x):
        return self.block(x)

# acronym for easy load
class _Net(FCN):
    def __init__(self, args):
        super(_Net, self).__init__(args.nclass, args.backbone, args.norm_layer)