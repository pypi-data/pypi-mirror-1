from tgcaptcha import controller
import unittest
from turbogears import controllers, startup, testutil, config, database
import cherrypy

config.update({"tgcaptcha.key":"I have a secret."})

class TestController(unittest.TestCase):
    
    def setUp(self):
        config.update({"sqlobject.dburi":"sqlite:///:memory:",
                        "visit.on":"True",
                        "tgcaptcha.controller": "/captcha"})
        cherrypy.root = Root()
        
    def test_make_plaintext(self):
        c = controller.CaptchaController()
        txt = c.text_generator()
        self.assertEqual(len(txt), 5)
        
    def test_image(self):
        c = controller.CaptchaController()
        p = c.create_payload()
        testutil.createRequest("/captcha/image/%s" % p)
        response = cherrypy.response
        self.assertEqual(response.status, '200 OK', response.body[0])
        self.assertEqual(response.headers['Content-Type'], 'image/jpeg')
        
    def test_complex_controller_cfg(self):
        config.update({'tgcaptcha.controller':'/some/silly/captcha'})
        c = controller.CaptchaController()
        p = c.create_payload()
        testutil.createRequest('/some/silly/captcha/image/%s' % p)
        response = cherrypy.response
        self.assertEqual(response.status, '200 OK', response.body[0])
        self.assertEqual(response.headers['Content-Type'], 'image/jpeg')     
        
    def tearDown(self):
        startup.stopTurboGears()
        
class Root(controllers.RootController):
    
    some = controllers.Controller()
    some.silly = controllers.Controller()
        