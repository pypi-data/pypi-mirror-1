from django.test import TestCase
from django.contrib.auth.models import User as AuthUser

class TestRunner(TestCase):
    username = 'josh'
    password = 'qwerty'

    def create_test_user(self):
        testUser =  AuthUser.objects.create_user(self.username, 
                                                 'temp@gmail.com',
                                                 self.password,
                   )
        testUser.is_staff = True
        testUser.is_superuser = True
        testUser.save()
        return testUser 


