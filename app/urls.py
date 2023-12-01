from django.urls import path ,re_path
from .views import *
urlpatterns = [
    path('' , home),
    path('java/', javaRequest),
    path('getToken/' , getToken),
    path('getData/' ,getData),
    path('sendData/' ,getZipFiles),
    path('signin/' ,createAccountPage),
    path('createAccount/' ,createAccount),
    path('tjson/' ,sendJson),
    path('checkCredential/' ,javaSignIn),
    path('data/' ,getUserFiles),

    re_path('checkconnection/' ,checkConnection),
    re_path('testSignup/' ,signupTest),
    re_path('loginsite/' ,loginApi),
    re_path('test_token/' ,test_token),
    path("getCorrectToken/" ,get_csrf_token),
    path('LoginIn' ,loginAccount),
    path("lol/" ,saveFiles),
]
