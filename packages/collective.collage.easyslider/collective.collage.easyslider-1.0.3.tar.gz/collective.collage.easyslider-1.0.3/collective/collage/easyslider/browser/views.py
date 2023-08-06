# -*- coding: utf-8 -*-
'''
Created on 11/12/2009

@author: jpg
'''
from Products.Collage.browser.views import BaseView
from collective.easyslider.browser.views import SliderView

class EasySliderView(SliderView, BaseView):
    """ Collage view implementing jQuery Easy Slider
    """
    