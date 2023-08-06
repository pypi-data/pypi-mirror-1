#coding: utf-8
'''
    To add image gallery for your model you should complete following steps:
    
    1. Create album site instance and plug it's urls to urlconf::
    
        from photo_albums.urls import PhotoAlbumSite
        accounts_photo_site = PhotoAlbumSite(instance_name = 'user_images', 
                                 queryset = User.objects.all(), 
                                 template_object_name = 'album_user',
                                 has_edit_permission = lambda request, obj: request.user==obj) 
        urlpatterns += patterns('', url(r'^accounts/', include(accounts_photo_site.urls)),)
    
    Please note that if you deploy multiple albums (ex. for different models), 
    you must provide unique ``instance_name`` for each instance to make url 
    reversing work.
    
    Included urls looks like ``<object_id>/<app_name>/<action>`` or 
    ``<object_id>/<app_name>/<image_id>/<action>``,
    where object_id is the id of object which is gallery attached to, 
    app_name is "albums" by default, image_id is image id :) and action 
    is performed action (view, edit, etc). It is possible to use slug 
    instead of object's id (look at ``object_regex`` and ``lookup_field`` 
    parameters). 
    
    2. Create the necessary templates. 
       
    3. Link people to image gallery using ``{% url .. %}`` template tags.
    
    You can use these urls (assuming that `user_images` in an instance name,
    `album_user` is object for which gallery is attached to, `image` is image 
    in gallery)::
    
        {% url user_images:show_album album_user.id %}
        
        {% url user_images:edit_album album_user.id %}
        
        {% url user_images:upload_main_image album_user.id %}
        
        {% url user_images:upload_images album_user.id %}
        
        {% url user_images:show_image album_user.id image.id %}
        
        {% url user_images:edit_image album_user.id image.id %}
        
        {% url user_images:delete_image album_user.id image.id %}
        
        {% url user_images:set_as_main_image album_user.id image.id %}
        
        {% url user_images:clear_main_image album_user.id image.id %}
        
        {% url user_images:reorder_images album_user.id %}
        
        {% url user_images:set_image_order album_user.id %}
        
'''

from django.conf.urls.defaults import *
from generic_utils.app_utils import PluggableSite
from photo_albums.forms import ImageEditForm, PhotoFormSet
from generic_images.forms import AttachedImageForm

class PhotoAlbumSite(PluggableSite):
    '''
        Constructor parameters:
        
        ``instance_name``: String. Required. App instance name for url 
        reversing. Must be unique.
        
        ``queryset``: QuerySet. Required. Albums will be attached to objects 
        in this queryset.
        
        ``object_regex``: String. Optional, default is '\d+'. It should be a 
        URL regular expression for object in URL. You should use smth. 
        like '[\w\d-]+' for slugs.
        
        ``lookup_field``: String. Optional, default is 'pk'. It is a field 
        name to lookup. It may contain ``__`` and follow relations 
        (ex.: `userprofile__slug`).
        
        ``app_name``: String. Optional, default value is 'album'. Used by url 
        namespaces stuff.
        
        ``extra_context``: Dict. Optional. Extra context that will be passed 
        to each view.
        
        ``template_object_name``: String. Optional. The name of template 
        context variable with object for which album is attached. 
        Default is 'object'.
        
        ``has_edit_permission``: Optional. Function that accepts request and 
        object and returns True if user is allowed to edit album for 
        object and False otherwise. Default behaviour is to always 
        return True.
        
        ``context_processors``: Optional. A list of callables that will be 
        used as additional context_processors in each view    

        ``edit_form_class``: Optional. ModelForm subclass to be used in 
        edit_image view
        
        ``upload_form_class``: Optional. ModelForm subclass to be used in 
        upload_main_image view
        
        ``upload_formset_class``: Optional. ModelFormSet to be used in 
        upload_images view
        
    '''        
                    
    def __init__(self, instance_name, queryset, app_name='album', 
                 object_regex = r'\d+', lookup_field = 'pk',                 
                 extra_context=None, template_object_name = 'object',
                 has_edit_permission = lambda request, obj: True,
                 context_processors=None,
                 edit_form_class = ImageEditForm,
                 upload_form_class = AttachedImageForm,
                 upload_formset_class = PhotoFormSet):
        self.edit_form_class = edit_form_class
        self.upload_form_class = upload_form_class
        self.upload_formset_class = upload_formset_class
            
        super(PhotoAlbumSite, self).__init__(instance_name, queryset, app_name, 
                                             object_regex, lookup_field,                                             
                                             extra_context, template_object_name,
                                             has_edit_permission, context_processors)
                
    def patterns(self):
        return patterns('photo_albums.views',
                        
                        #album-level views
                        url(
                            self.make_regex(r'/'),
                            'show_album', 
                            {'album_site': self},
                            name = 'show_album',
                        ),
                        url(
                            self.make_regex(r'/edit'),
                            'edit_album', 
                            {'album_site': self},
                            name = 'edit_album',
                        ),
                        url(
                            self.make_regex(r'/upload_main/'),                            
                            'upload_main_image',
                            {'album_site': self},
                            name = 'upload_main_image',
                        ),
                        url(
                            self.make_regex(r'/upload_images/'),
                            'upload_images',
                            {'album_site': self},
                            name = 'upload_images',
                        ),
                        
                        
                        #one image views
                        url(
                            self.make_regex(r'/(?P<image_id>\d+)/'),
                            'show_image',
                            {'album_site': self},
                            name = 'show_image',
                        ),
                        url(
                            self.make_regex(r'/(?P<image_id>\d+)/edit'),
                            'edit_image',
                            {'album_site': self},
                            name = 'edit_image',
                        ),
                        url(
                            self.make_regex(r'/(?P<image_id>\d+)/delete'),
                            'delete_image',
                            {'album_site': self},
                            name = 'delete_image',
                        ),
                        url(
                            self.make_regex(r'/(?P<image_id>\d+)/set-as-main'),
                            'set_as_main_image',
                            {'album_site': self},
                            name = 'set_as_main_image',
                        ),
                        url(
                            self.make_regex(r'/(?P<image_id>\d+)/clear-main'),
                            'clear_main_image',
                            {'album_site': self},
                            name = 'clear_main_image',
                        ),
                                                
                        #reorder
                        url(
                            self.make_regex(r'/reorder/'),
                            'edit_album', 
                            {'album_site': self, 'template_name': 'reorder_images.html'},
                            name = 'reorder_images',
                        ),
                        url(
                            self.make_regex(r'/set_image_order'),
                            'set_image_order', 
                            {'album_site': self},
                            name = 'set_image_order',
                        ),
                    )                    
   
