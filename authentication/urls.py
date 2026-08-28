from django.urls import path

from .views import (
    test_authentication,
    register,
    user_login,
    role_selection,
    user_logout,
)


urlpatterns = [

    path(
        'test/',
        test_authentication,
        name='test_authentication'
    ),

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'login/',
        user_login,
        name='login'
    ),

    path(
        'roles/',
        role_selection,
        name='role_selection'
    ),

    path(
        'logout/',
        user_logout,
        name='logout'
    ),

]