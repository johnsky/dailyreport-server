# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from jsonrpc import jsonrpc_method
from dailyreport.user_profile.models import UserProfile
from django.conf import settings
from permissions.models import Role, PrincipalRoleRelation

@jsonrpc_method('userProfile.getClientVersion', authenticated=True)
def get_client_version(request):
    """
    Получить версию клиента
    """
    profile = UserProfile.objects.get(user=request.user)
    print profile
    print profile.client_version
    return profile.client_version
    
@jsonrpc_method('userProfile.setClientVersion', authenticated=True)
def set_client_version(request, version):
    """
    Установить версию клиента
    """
    profile = UserProfile.objects.get(user=request.user)
    profile.client_version = version
    profile.save(force_update=True)
    print version
    return version

@jsonrpc_method('userProfile.IsManager', authenticated=True)
def get_is_manager(request):
    """
    """
    try:
        print PrincipalRoleRelation.objects.filter(Q(user = request.user) | Q(group__in = request.user.groups.all()),
                                                role__name = settings.ROLE_MANAGER_NAME)
        print 
        
        if PrincipalRoleRelation.objects.filter(Q(user = request.user) | Q(group__in = request.user.groups.all()),
                                                role__name = settings.ROLE_MANAGER_NAME).count() > 0:
            return {'manager': True}
        else:
            if PrincipalRoleRelation.objects.filter(Q(user = request.user) | Q(group__in = request.user.groups.all()),
                                                    role__name = settings.ROLE_ADMIN_NAME).count() > 0:
                return {'manager': True}
            else: 
                return {'manager': False}
    except Exception as ex:
        print ex
        return {'manager': False}
    
@jsonrpc_method('userProfile.IsAdmin', authenticated=True)
def get_is_admin(request):
    """
    """
    if PrincipalRoleRelation.objects.filter(Q(user = request.user) | Q(group__in = request.user.groups.all()),
                                            role__name = settings.ROLE_ADMIN_NAME).count() > 0:
        return {'admin': True}
    else:
        return {'admin': False}

@jsonrpc_method('userProfile.IsDeveloper', authenticated=True)
def get_is_developer(request):
    """
    """
    if PrincipalRoleRelation.objects.filter(Q(user = request.user) | Q(group__in = request.user.groups.all()),
                                            role__name = settings.ROLE_DEVELOPER_NAME).count() > 0:
        return {'developer':True}
    else:
        return {'developer': False}

@jsonrpc_method('userProfile.getUserRoles', authenticated=True)
def get_user_roles(request):
    import permissions
    import permissions.utils
    
    user_roles = []
    roles = permissions.utils.get_roles(request.user)
    for role in roles:
        item = {'id': role.id, 'name': role.name}
        user_roles.append(item)   

    return user_roles

@jsonrpc_method('userProfile.getApplicationPermissions', authenticated=True)
def get_app_permissions(request):
    from permissions.models import Permission
    permissions_list = list(Permission.objects.values('id','name'))
   
    return permissions_list
