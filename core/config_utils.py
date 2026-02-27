from .models import SystemConfig


def axes_whitelist(request, credentials):
    """
    Isenta superusuários do bloqueio do django-axes.
    Retorna True para liberar o acesso (não bloquear), False para aplicar o bloqueio normal.
    O axes chama esta função com (request, credentials).
    """
    from django.contrib.auth.models import User
    username = (credentials or {}).get('username', '')
    if not username:
        username = (
            request.POST.get('username', '')
            or request.GET.get('username', '')
        )
    username = (username or '').strip()
    if not username:
        return False
    try:
        user = User.objects.get(username=username)
        return user.is_superuser and user.is_active
    except User.DoesNotExist:
        return False


def get_config(key, default=''):
    try:
        return SystemConfig.objects.get(key=key).value
    except SystemConfig.DoesNotExist:
        return default


def set_config(key, value):
    SystemConfig.objects.update_or_create(key=key, defaults={'value': str(value) if value is not None else ''})


def get_all_configs(keys):
    """Return a dict of {key: value} for a list of keys."""
    rows = SystemConfig.objects.filter(key__in=keys).values_list('key', 'value')
    result = {k: '' for k in keys}
    result.update(dict(rows))
    return result
