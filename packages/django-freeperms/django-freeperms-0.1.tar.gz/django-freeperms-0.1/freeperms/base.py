from django.conf import settings
from django.contrib import auth
from django.contrib.auth import models
from django.db.models import manager


_anonymous_perms = set()

def register(perm):
    """
    Register a permission.

    Permission is in the form `app_label.code_name` identical to
    `User.has_perm` or `User.has_module_perm`.
    """
    global _anonymous_perms
    _anonymous_perms.add(perm)


def unregister(perm):
    """
    Unregister a permission.
    """
    global _anonymous_perms
    if perm in _anonymous_perms:
        _anonymous_perms.remove(perm)


class AnonymousPermissionsManager(manager.Manager):
    anonymous_perms = _anonymous_perms

    def select_related(self):
        perms = list()
        for perm in self.anonymous_perms:
            app_label, codename = perm.split('.')
            try:
                perms.append(models.Permission.objects.get(
                    content_type__app_label=app_label, codename=codename))
            except models.Permission.DoesNotExist: pass
        return perms


class PermissibleAnonymousUser(models.AnonymousUser):
    _user_permissions = AnonymousPermissionsManager()
    username = getattr(settings, 'ANONYMOUS_USERNAME', 'anonymous')

    def has_perms(self, perm_list):
        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True

    def has_perm(self, perm):
        for backend in auth.get_backends():
            if hasattr(backend, "has_perm"):
                if backend.has_perm(self, perm):
                    return True
        return False

    def has_module_perms(self, app_label):
        for backend in get_backends():
            if hasattr(backend, "has_module_perms"):
                if backend.has_module_perms(self, app_label):
                    return True
        return False

    def get_all_permissions(self):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(self))
        return permissions 
