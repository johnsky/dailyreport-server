# -*- coding: utf-8 -*-

from jsonrpc import jsonrpc_method
from django.core import serializers

@jsonrpc_method('auth.logIn')
def log_in(request, user_name, password):
    # Если пользователь уже авторизован, тогда возвращаем ошибку
    if request.user.is_anonymous() == False :
        raise Exception(u'Пользователь уже авторизован')
    
    from django.contrib.auth import authenticate, login
    
    user = authenticate(username=user_name, password=password)
    
    if user is None:
        raise Exception(u'Неверный пользователь/пароль')
    
    if not user.is_active:
        raise Exception(u'Вход не выполнен, пользователь не активен')

    login(request, user)
    #user_groups = list(user.groups.all().values_list('name', flat=True))

    user_model={}
        
    user_model['userName']   = user.username
    user_model['superUser']  = user.is_superuser
    user_model['firstName']  = user.first_name
    user_model['lastName']   = user.last_name
    
    print user_model

    return user_model                        

@jsonrpc_method('auth.logOut', authenticated=True)
def log_out(request):
    from django.contrib.auth import logout
    if request.user.is_anonymous() == False :
        logout(request)
    else:
        raise Exception(u'Пользователь не авторизован, невозможно сделать logOut.')

    return {'message': u'Пользователь завершил сессию.'}

@jsonrpc_method('auth.isAuthenticated')
def user_is_authenticated(request):
    """
    Проверка авторизации пользователя
    """
    #print serializers.serialize("json", request.user.groups.all())
        
    if request.user.is_authenticated():
        #from django.core import serializers
        #print serializers.serialize("json", request.user.groups.all())
        #print serializers.serialize("json", request.user.permissions.all()) 
        #user_groups = list(request.user.groups.all().values_list('name', flat=True))
        
        user_model={}
        
        user_model['userName']   = request.user.username
        user_model['superUser']  = request.user.is_superuser
        user_model['firstName']  = request.user.first_name
        user_model['lastName']   = request.user.last_name
        
        #user_model['groups']     =request.user.groups
        #user_model['permissions']=request.user.user_permissions
        
        return user_model
    
    return None

@jsonrpc_method('auth.getUsers', authenticated=True, safe=True)
def get_users(request):
    """
    
    """
    return {}
    
    