from test_setup import TestRunner
from django.db import IntegrityError 
from encrypt.models import Encrypt

class ViewTests(TestRunner):
    def test_add_encrypt(self):
        '''
        Simple create new encypted location
        '''

        User = self.create_test_user()
        encrypt = Encrypt(user = User, name = 'temp')
        encrypt_text = ['randomness','ok',{'ok':'dokey'}]
        encrypt.set(self.password, encrypt_text)
        result = encrypt.get(self.password)
	self.assertEqual(encrypt_text, result)

    def test_unique_name_user(self):
	self.test_add_encrypt()
        self.assertRaises(IntegrityError, self.test_add_encrypt)
