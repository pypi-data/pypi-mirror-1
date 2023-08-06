from django.conf import settings

from freeperms import base


class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            from django.contrib.auth import get_user
            request._cached_user = get_user(request)
        if not request._cached_user.is_authenticated():
            request._cached_user = base.PermissibleAnonymousUser()
        return request._cached_user


class AnonymousPermissionsMiddleware(object):
    def process_request(self, request):
        anonymous_permissions = getattr(
            settings, 'ANONYMOUS_PERMISSIONS', [])
        
        if not request.user.is_authenticated() and anonymous_permissions:
            request.__class__.user = LazyUser()

        if anonymous_permissions and not base._anonymous_perms:
            map(lambda perm: base.register(perm), anonymous_permissions)
