from django.test import TestCase

class UrlTest(TestCase):
    fixtures = ['testdata.json']

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_settings(self):
        response = self.client.get('/settings/')
        self.assertEqual(response.status_code, 200)
        
    def test_getServerStatus(self):
        response = self.client.get('/getServerStatus/')
        self.assertEqual(response.status_code, 200)
        
    def test_hostsList(self):
        response = self.client.get('/hostsList/')
        self.assertEqual(response.status_code, 200)
        
    def test_hosts(self):
        response = self.client.get('/hosts/')
        self.assertEqual(response.status_code, 200) 
        
    def test_resources(self):
        response = self.client.get('/resources/')
        self.assertEqual(response.status_code, 200) 
        
    def test_connectivity(self):
        response = self.client.get('/connectivity/')
        self.assertEqual(response.status_code, 200) 
                        
    def test_resourceList(self):
        response = self.client.get('/resourceList/')
        self.assertEqual(response.status_code, 200)
          
    def test_handlers(self):
        response = self.client.get('/handlers/')
        self.assertEqual(response.status_code, 200)

    def test_resource(self):
        response = self.client.get('/resource/1')
        self.assertEqual(response.status_code, 200) 
        
        response = self.client.get('/resource/10000')
        self.assertEqual(response.status_code, 404)         

    def test_resource_status(self):
        response = self.client.get('/resourceStatus/1')
        self.assertEqual(response.status_code, 200) 

    def test_subList(self):
        response = self.client.get('/subList/10', follow=True)
        self.assertEqual(response.status_code, 200)
