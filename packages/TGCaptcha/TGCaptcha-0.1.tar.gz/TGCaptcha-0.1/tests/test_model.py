from tgcaptcha import model
import unittest
from datetime import datetime

class ModelTest(unittest.TestCase):
    
    def test_created_set(self):
        t0 = datetime.utcnow()
        p = model.Captcha('foobar')
        t1 = datetime.utcnow()
        self.assert_(t0 < p.created)
        self.assert_(t1 > p.created)
    
    def test_serialization(self):
        p = model.Captcha('foobar')
        s = p.serialize()
        p_new = model.Captcha.deserialize(s)
        self.assertEqual('foobar', p_new.plaintext)
        self.assertEqual(p.created.timetuple()[:6], 
                p_new.created.timetuple()[:6])
        