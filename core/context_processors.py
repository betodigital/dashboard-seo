def system_config(request):
    """Injeta configurações gerais do sistema em todos os templates."""
    from .config_utils import get_config
    return {
        'system_name': get_config('system_name', 'MyApp') or 'MyApp',
    }


def user_permissions(request):
    """Injeta as permissões de tela do usuário em todos os templates."""
    if not request.user.is_authenticated:
        return {'perms_map': {}}

    if request.user.is_superuser:
        perms = {
            'dashboard': True,
            'reports':   True,
            'settings':  True,
            'users':     True,
        }
    else:
        try:
            p = request.user.profile
            perms = {
                'dashboard': p.can_view_dashboard,
                'reports':   p.can_view_reports,
                'settings':  p.can_view_settings,
                'users':     p.can_view_users,
            }
        except Exception:
            perms = {'dashboard': True, 'reports': False, 'settings': False, 'users': False}

    return {'perms_map': perms}
