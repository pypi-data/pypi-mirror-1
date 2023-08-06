'''
Views for use with PhotoAlbumSite. 
'''

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.create_update import create_object, delete_object, update_object
from django.utils import simplejson
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType

from annoying.decorators import ajax_request
from annoying.utils import HttpResponseReload

from photo_albums.forms import PhotoFormSet
from generic_images.forms import AttachedImageForm
from generic_images.models import AttachedImage
from generic_utils import get_template_search_list


def _get_template_names(object, template_name):
    return get_template_search_list('albums', object, template_name)
     

def show_album(request, object_id, album_site, template_name='show_album.html'):
    ''' Show album for object using show_album.html template '''
        
    object, context = album_site.get_object_and_context(object_id)
    
    images = AttachedImage.objects.for_model(object)
    context.update({'images': images})
    return render_to_response(_get_template_names(object, template_name), 
                              context,
                              context_instance=RequestContext(request, processors=album_site.context_processors),
                              )
    

@login_required
def edit_album(request, object_id, album_site, template_name='edit_album.html'):
    ''' same as ``show_album`` view but with login_required decorator '''
    
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    images = AttachedImage.objects.for_model(object)
    context.update({'images': images})
        
    return render_to_response(_get_template_names(object, template_name), 
                              context,
                              context_instance=RequestContext(request, processors=album_site.context_processors),
                              )
    
    
@login_required
def upload_main_image(request, object_id, album_site):    
    ''' upload 1 image and make it main image in gallery '''
    
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    success_url = album_site.reverse('show_album', args=[object_id])
    
    if request.method == 'POST':
        form = album_site.upload_form_class(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.content_object = object
            photo.is_main = True
            photo.save()
            return HttpResponseRedirect(success_url) # Redirect after POST
    else:
        form = album_site.upload_form_class()        

    context.update({'form': form})

    return render_to_response(
                                _get_template_names(object, 'upload_main_image.html'),
                                context,
                                context_instance=RequestContext(request, processors=album_site.context_processors),
                             )


@login_required
def upload_images(request, object_id, album_site):    
    ''' upload several images at once '''
    
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    success_url = album_site.reverse('show_album', args=[object_id])
    
    if request.method == 'POST':
        formset = album_site.upload_formset_class(request.POST, request.FILES, queryset = AttachedImage.objects.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for photo in instances:
                photo.user = request.user
                photo.content_object = object
                photo.save()
            return HttpResponseRedirect(success_url) # Redirect after POST
    else:
        formset = album_site.upload_formset_class(queryset = AttachedImage.objects.none())        

    context.update({'formset': formset})
    
    return render_to_response(_get_template_names(object, 'upload_images.html'), 
                              context, 
                              context_instance=RequestContext(request, processors=album_site.context_processors))



def _one_image_context(image_id, object):
    album = AttachedImage.objects.for_model(object) 
    image = get_object_or_404(album, id=image_id)    

    next_id = getattr(image.next(), 'id', None)
    prev_id = getattr(image.previous(), 'id', None)
    
    return {'image': image, 'prev': prev_id, 'next': next_id}


def show_image(request, object_id, image_id, album_site):
    '''  show one image '''
    
    object, context = album_site.get_object_and_context(object_id)        
    context.update(_one_image_context(image_id, object))

    return render_to_response(_get_template_names(object, 'show_image.html'), context, 
                              context_instance=RequestContext(request, processors=album_site.context_processors))


@login_required
def edit_image(request, object_id, image_id, album_site): 
    ''' show one image, use login_required decorator and provide edit form '''   
    
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)

    context.update(_one_image_context(image_id, object))

    if request.method == 'POST':
        form = album_site.edit_form_class(request.POST, request.FILES, instance = context['image'])
        if form.is_valid():
            form.save()
            return HttpResponseReload(request) # Redirect after POST
    else:
        form = album_site.edit_form_class(instance = context['image'])
        
    context.update({'form': form})
    
    return render_to_response(_get_template_names(object, 'edit_image.html'), context, 
                              context_instance=RequestContext(request, processors=album_site.context_processors))
    

@login_required
def delete_image(request, object_id, image_id, album_site):
    ''' delete image if request method is POST, displays 
        ``confirm_delete.html`` template otherwise 
    '''
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    image = get_object_or_404(AttachedImage.objects.for_model(object), id=image_id)
    next_url = album_site.reverse('show_album', args=[object_id])
    
    return delete_object(request, 
                         model=AttachedImage, 
                         post_delete_redirect = next_url, 
                         object_id = image_id,
                         extra_context = context, 
                         context_processors=album_site.context_processors,
                         template_name = _get_template_names(object, 'confirm_delete.html')[1])


    
@login_required
def set_as_main_image(request, object_id, image_id, album_site):
    ''' mark image as main and redirect to ``show_image`` view '''
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    image = get_object_or_404(AttachedImage.objects.for_model(object), id=image_id)
    image.is_main = True
    image.save()
    
    next_url = album_site.reverse('show_image', args=[object_id, image_id])    
    return HttpResponseRedirect(next_url)

    
@login_required
def clear_main_image(request, object_id, image_id, album_site):
    ''' mark image as not main and redirect to ``show_image`` view '''
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)

    image = AttachedImage.objects.get_main_for(object)
    if image:
        image.is_main = False
        image.save()
        
    next_url = album_site.reverse('show_image', args=[object_id, image_id])    
    return HttpResponseRedirect(next_url)


@login_required
@ajax_request
def set_image_order(request, object_id, album_site):
    ''' Ajax view that can be used to implement image reorder
    functionality. Accepts json data in form:: 
    
        {'items': '[
                        {"id":"<id1>", "order":"<order1>"},
                        {"id":"<id2>", "order":"<order2>"}, 
                        ...
                    ]'
        }
            
    and assigns passed order to images with passed id's, with permission checks. 
    '''
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    if request.is_ajax():        
        data_str = request.POST.get('items','')
        items = simplejson.loads(data_str)
        for item in items:
            image_id = item['id']
            order = item['order']
            try:
                #check that image belongs to proper object
                image = AttachedImage.objects.for_model(object).get(id=image_id)
                image.order = order
                image.save()
            except AttachedImage.DoesNotExist:
                return {'done': False, 'reason': 'Invalid data.'}            
        return {'done': True}
    raise Http404
