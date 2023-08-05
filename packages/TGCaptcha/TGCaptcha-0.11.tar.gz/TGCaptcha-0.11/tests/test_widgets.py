from tgcaptcha import widgets
import unittest
import turbogears as tg
import re

class WidgetsTest(unittest.TestCase):
    
    def setUp(self):
        tg.config.update({'tgcaptcha.key': 'Woot Woot'})
    
    def test_create_captcha_field(self):
        cf = widgets.CaptchaField(name="test")
        r  = cf.render()
        self.assert_('<INPUT NAME="test.captchahidden"' in r)
        self.assert_('NAME="test.captchainput"' in r)
        
    def test_captchafield_payload(self):
        "Payload occurs twice in the CaptchaField."
        cf = widgets.CaptchaField(name="test")
        r  = cf.render()
        # find the payload
        pat = '"(?P<payload>\S{43}=)"'
        s = re.search(pat, r)
        self.assertEqual(len(s.group('payload')), 44)
        self.assertEqual(r.count(s.group('payload')), 2)
        
    def test_set_params(self):
        "Widget params are still settable."
        cf = widgets.CaptchaField(name="test")
        r = cf.render(alt={'captchainput':'squint'})
        self.assert_('ALT="squint"' in r)
        self.assert_('ALT="obfuscated letters"' not in r)