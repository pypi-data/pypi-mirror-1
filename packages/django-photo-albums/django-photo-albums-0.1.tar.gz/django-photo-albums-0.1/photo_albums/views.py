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

from photo_albums.forms import PhotoFormSet
from generic_images.forms import AttachedImageForm
from generic_images.models import AttachedImage
from generic_utils import get_template_search_list


def get_template_names(object, template_name):
    return get_template_search_list('albums', object, template_name)
     

def show_album(request, object_id, album_site, template_name='show_album.html'):
        
    object, context = album_site.get_object_and_context(object_id)
    
    images = AttachedImage.objects.get_for_model(object)
    context.update({'images': images})
    return render_to_response(get_template_names(object, template_name), 
                              context,
                              context_instance=RequestContext(request),
                              )
    

@login_required
def edit_album(request, object_id, album_site, template_name='edit_album.html'):
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    images = AttachedImage.objects.get_for_model(object)
    context.update({'images': images})
        
    return render_to_response(get_template_names(object, template_name), 
                              context,
                              context_instance=RequestContext(request),
                              )
    
    
@login_required
def upload_main_image(request, object_id, album_site):    

    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    success_url = album_site.reverse('show_album', args=[object_id])
    
    if request.method == 'POST':
        form = AttachedImageForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.content_object = object
            photo.is_main = True
            photo.save()
            return HttpResponseRedirect(success_url) # Redirect after POST
    else:
        form = AttachedImageForm()        

    context.update({'form': form})

    return render_to_response(
                                get_template_names(object, 'upload_main_image.html'),
                                context,
                                context_instance=RequestContext(request),
                             )


@login_required
def upload_images(request, object_id, album_site):    
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    success_url = album_site.reverse('show_album', args=[object_id])
    
    if request.method == 'POST':
        formset = PhotoFormSet(request.POST, request.FILES, queryset = AttachedImage.objects.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for photo in instances:
                photo.user = request.user
                photo.content_object = object
                photo.save()
            return HttpResponseRedirect(success_url) # Redirect after POST
    else:
        formset = PhotoFormSet(queryset = AttachedImage.objects.none())        

    context.update({'formset': formset})
    
    return render_to_response(get_template_names(object, 'upload_images.html'), 
                              context, 
                              context_instance=RequestContext(request))


def show_image(request, object_id, image_id, album_site, template_name = 'show_image.html'):
    object, context = album_site.get_object_and_context(object_id)
    
    images = AttachedImage.objects.get_for_model(object) 
    image = get_object_or_404(images, id=image_id)    
    
    try:
        next_id = images.filter(order__lt=image.order).order_by('-order')[0].id
    except IndexError:
        next_id = None
    
    try:    
        prev_id = images.filter(order__gt=image.order).order_by('order')[0].id    
    except IndexError:
        prev_id = None

    context.update({'image': image, 'prev': prev_id, 'next': next_id})

    return render_to_response(get_template_names(object, template_name), 
                              context, 
                              context_instance=RequestContext(request))


@login_required
def edit_image(request, object_id, image_id, album_site):    
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    return show_image(request, object_id, image_id, album_site, template_name='edit_image.html')


@login_required
def delete_image(request, object_id, image_id, album_site):
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    image = get_object_or_404(AttachedImage.objects.get_for_model(object), id=image_id)
    next_url = album_site.reverse('show_album', args=[object_id])
    
    return delete_object(request, 
                         model=AttachedImage, 
                         post_delete_redirect = next_url, 
                         object_id = image_id,
                         extra_context = context, 
                         template_name = get_template_names(object, 'confirm_delete.html')[1])


    
@login_required
def set_as_main_image(request, object_id, image_id, album_site):
    object, context = album_site.get_object_and_context(object_id)
    album_site.check_permissions(request, object)
    
    image = get_object_or_404(AttachedImage.objects.get_for_model(object), id=image_id)
    image.is_main = True
    image.save()
    
    next_url = album_site.reverse('show_image', args=[object_id, image_id])    
    return HttpResponseRedirect(next_url)

    
@login_required
def clear_main_image(request, object_id, image_id, album_site):
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
                image = AttachedImage.objects.get_for_model(object).get(id=image_id)
                image.order = order
                image.save()
            except AttachedImage.DoesNotExist:
                return {'done': False, 'reason': 'Invalid data.'}            
        return {'done': True}
    raise Http404
