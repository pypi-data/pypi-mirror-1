from django.db import models
from django.contrib.auth.models import User

from pyRijndael import EncryptData, DecryptData
import cPickle as pickle

class Encrypt(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    text = models.TextField()

    class Meta:
        unique_together = [("user", "name")]

    def set(self, password, obj):
        '''
        Setting an encrypted object.
        '''
        if self.user.check_password(password) == True:
            self.text = pickle.dumps(EncryptData(password, 
                                                 pickle.dumps(obj)))
            self.save()
        return 0 # Everything ok

    def get(self, password):
        '''
        Retreving an encrypted object.
        '''
        if self.user.check_password(password) == True:
            return pickle.loads(DecryptData(password, 
                                            pickle.loads(self.text)))
