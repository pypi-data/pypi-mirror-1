#coding: utf-8

from django.conf.urls.defaults import *
from generic_utils.app_utils import PluggableSite

class PhotoAlbumSite(PluggableSite):
    
    def __init__(self, instance_name, queryset, app_name='album', 
                 extra_context=None, template_object_name = 'object',
                 has_edit_permission = lambda request, obj: True):
        
        super(PhotoAlbumSite, self).__init__(instance_name, queryset, app_name, 
                                             extra_context, template_object_name,
                                             has_edit_permission)
                
    def patterns(self):
        return patterns('photo_albums.views',
                        
                        #album-level views
                        url(
                            r'^(?P<object_id>\d+)/%s/$' % self.app_name,
                            'show_album', 
                            {'album_site': self},
                            name = 'show_album',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/edit$' % self.app_name,
                            'edit_album', 
                            {'album_site': self},
                            name = 'edit_album',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/upload_main/$' % self.app_name,
                            'upload_main_image',
                            {'album_site': self},
                            name = 'upload_main_image',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/upload_images/$' % self.app_name,
                            'upload_images',
                            {'album_site': self},
                            name = 'upload_images',
                        ),
                        
                        
                        #one image views
                        url(
                            r'^(?P<object_id>\d+)/%s/(?P<image_id>\d+)/$' % self.app_name,
                            'show_image',
                            {'album_site': self},
                            name = 'show_image',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/(?P<image_id>\d+)/edit$' % self.app_name,
                            'edit_image',
                            {'album_site': self},
                            name = 'edit_image',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/(?P<image_id>\d+)/delete$' % self.app_name,
                            'delete_image',
                            {'album_site': self},
                            name = 'delete_image',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/(?P<image_id>\d+)/set-as-main$' % self.app_name,
                            'set_as_main_image',
                            {'album_site': self},
                            name = 'set_as_main_image',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/(?P<image_id>\d+)/clear-main$' % self.app_name,
                            'clear_main_image',
                            {'album_site': self},
                            name = 'clear_main_image',
                        ),
                                                
                        #reorder
                        url(
                            r'^(?P<object_id>\d+)/%s/reorder/$' % self.app_name,
                            'edit_album', 
                            {'album_site': self, 'template_name': 'reorder_images.html'},
                            name = 'reorder_images',
                        ),
                        url(
                            r'^(?P<object_id>\d+)/%s/set_image_order$' % self.app_name,
                            'set_image_order', 
                            {'album_site': self},
                            name = 'set_image_order',
                        ),
                    )                    
   