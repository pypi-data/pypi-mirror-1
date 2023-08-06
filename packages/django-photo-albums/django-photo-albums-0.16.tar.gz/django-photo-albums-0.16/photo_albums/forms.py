#coding: utf-8

from django import forms
from django.forms.models import modelformset_factory

from generic_images.models import AttachedImage

class ImageEditForm(forms.ModelForm):
    class Meta:
        model = AttachedImage
        fields = ['caption']
            

PhotoFormSet = modelformset_factory(AttachedImage, 
                                    extra=3, 
                                    fields = ['image', 'caption']
                                   )

