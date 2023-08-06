#coding: utf-8

from django import forms
from django.forms.models import modelformset_factory

from generic_images.models import AttachedImage
from generic_images.forms import AttachedImageForm


PhotoFormSet = modelformset_factory(AttachedImage, 
                                    extra=3, 
                                    fields = ['image', 'caption']
                                   )

