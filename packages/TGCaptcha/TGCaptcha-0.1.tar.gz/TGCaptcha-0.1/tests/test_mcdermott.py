import unittest
import os
import tgcaptcha.plugins.image.mcdermott

gen_captcha = tgcaptcha.plugins.image.mcdermott.generate_jpeg

class CaptcaGenTest(unittest.TestCase):
    
    file_name = 'test_captcha.jpg'
    
    def tearDown(self):
        try:
            os.remove(self.file_name)
        except OSError:
            pass

    def test_createFile(self):
        gen_captcha('testme', self.file_name)
        self.failUnless(os.path.exists(self.file_name))
        
    def test_usingFileObj(self):
        f = open(self.file_name, 'wb')
        gen_captcha('testme', f)
        f.close()
        self.failUnless(os.path.exists(self.file_name))
        