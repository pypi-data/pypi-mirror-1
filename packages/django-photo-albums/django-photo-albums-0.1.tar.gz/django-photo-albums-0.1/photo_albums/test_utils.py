#coding: utf-8

from django.core.urlresolvers import reverse
from generic_utils.test_helpers import ViewTest
from generic_images.models import AttachedImage

class AlbumTest(ViewTest):
        
    username = None
    password = None
    fixtures = []
    album_site = None
    excluded_views = []
    
    album_for_id = None
    non_existing_object_id = 0
    
    image_in_album_id = None
    image2_in_album_id = None
    image_in_other_album_id = None
    non_existing_image_id = 0
    
    def check(self, view, status, kwargs=None):
        if not kwargs:
            kwargs = {}
        if view not in self.excluded_views:            
            if not 'object_id' in kwargs:
                kwargs['object_id'] = self.album_for_id
            name = '%s:%s' % (self.album_site.instance_name, view,)
            return self.check_url(name, status, kwargs=kwargs, current_app=self.album_site.app_name)                
                
    def test_public_views(self):
        self.check('show_album', 200)
        self.check('show_album', 404, kwargs={'object_id':self.non_existing_object_id})

        self.check('show_image', 200, kwargs={'image_id': self.image_in_album_id})
        self.check('show_image', 404, kwargs={'image_id': self.image_in_other_album_id})
        self.check('show_image', 404, kwargs={'image_id': self.non_existing_image_id})
        
    def test_forbidden_views(self):
        self.check('edit_album', 302)
        self.check('upload_main_image', 302)
        self.check('upload_images', 302)
        self.check('edit_image', 302, kwargs={'image_id': self.image_in_album_id})
        self.check('delete_image', 302, kwargs={'image_id': self.image_in_album_id})
        self.check('set_as_main_image', 302, kwargs={'image_id': self.image_in_album_id})
        self.check('clear_main_image', 302, kwargs={'image_id':  self.image_in_album_id})
        self.check('set_image_order', 302)
        
    def test_auth_views(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))

        self.check('edit_album', 200)
        self.check('upload_main_image', 200)
        self.check('upload_images', 200)
        self.check('show_album', 200)
        self.check('show_image', 200, kwargs={'image_id': self.image_in_album_id})
        
        self.check('reorder_images', 200)
        self.check('set_image_order', 404)

        self.check('edit_image', 200, kwargs={'image_id': self.image_in_album_id})
        self.check('delete_image', 200, kwargs={'image_id': self.image_in_album_id})
        self.check('set_as_main_image', 302, kwargs={'image_id': self.image_in_album_id})
        self.check('clear_main_image', 302, kwargs={'image_id': self.image_in_album_id})
        
    def test_reorder(self):
        if self.image2_in_album_id is None:
            return

        name = '%s:%s' % (self.album_site.instance_name, 'set_image_order',)
        url = reverse(name, kwargs={'object_id': self.album_for_id}, current_app = self.album_site.app_name)   
        
        img1 = AttachedImage.objects.get(id=self.image_in_album_id)
        img2 = AttachedImage.objects.get(id=self.image2_in_album_id)

        #correct:
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        response = self.client.post(url, 
                                   {'items': '[{"id":"%d","order":"%d"},{"id":"%d","order":"%d"}]' % 
                                               (img1.id, img2.order,img2.id, img1.order)}, 
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.content, '{"done": true}')
        
        img1_new = AttachedImage.objects.get(id=self.image_in_album_id)
        img2_new = AttachedImage.objects.get(id=self.image2_in_album_id)
        
        self.assertEqual(img1_new.id, img1.id)
        self.assertEqual(img1_new.order, img2.order)
        self.assertEqual(img2_new.id, img2.id)        
        self.assertEqual(img2_new.order, img1.order)