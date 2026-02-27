"""Utilitários para registrar eventos de acesso."""

def get_client_ip(request):
    """Extrai o IP real do cliente, suportando proxies."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def record_login_ok(request, user):
    from .models import AccessLog
    AccessLog.objects.create(
        user=user,
        username=user.username,
        event=AccessLog.EVENT_LOGIN_OK,
        ip_address=get_client_ip(request) or None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )


def record_login_fail(request, username):
    from .models import AccessLog
    AccessLog.objects.create(
        user=None,
        username=username or '(desconhecido)',
        event=AccessLog.EVENT_LOGIN_FAIL,
        ip_address=get_client_ip(request) or None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )


def record_logout(request, user):
    from .models import AccessLog
    AccessLog.objects.create(
        user=user,
        username=user.username,
        event=AccessLog.EVENT_LOGOUT,
        ip_address=get_client_ip(request) or None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )


def record_lockout(request, username):
    from .models import AccessLog
    AccessLog.objects.create(
        user=None,
        username=username or '(desconhecido)',
        event=AccessLog.EVENT_LOCKOUT,
        ip_address=get_client_ip(request) or None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )
