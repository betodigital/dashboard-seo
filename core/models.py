from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name  = models.CharField('Nome completo', max_length=150, blank=True)

    # Permissões de tela
    can_view_dashboard = models.BooleanField('Ver Dashboard',   default=True)
    can_view_reports   = models.BooleanField('Ver Relatórios',  default=False)
    can_view_settings  = models.BooleanField('Ver Configurações', default=False)
    can_view_users     = models.BooleanField('Gerenciar Usuários', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f'Perfil de {self.user.username}'

    def get_display_name(self):
        return self.full_name or self.user.get_full_name() or self.user.username

    # Superusuário tem acesso total
    def has_access(self, screen):
        if self.user.is_superuser:
            return True
        return getattr(self, f'can_view_{screen}', False)


class SystemConfig(models.Model):
    key        = models.CharField('Chave', max_length=100, unique=True, db_index=True)
    value      = models.TextField('Valor', blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Configuracao do Sistema'
        verbose_name_plural = 'Configuracoes do Sistema'

    def __str__(self):
        return self.key


class AccessLog(models.Model):
    EVENT_LOGIN_OK   = 'login_ok'
    EVENT_LOGIN_FAIL = 'login_fail'
    EVENT_LOGOUT     = 'logout'
    EVENT_LOCKOUT    = 'lockout'
    EVENT_CHOICES = [
        (EVENT_LOGIN_OK,   'Login bem-sucedido'),
        (EVENT_LOGIN_FAIL, 'Tentativa de login falha'),
        (EVENT_LOGOUT,     'Logout'),
        (EVENT_LOCKOUT,    'IP bloqueado'),
    ]

    user       = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='access_logs')
    username   = models.CharField(max_length=150)          # guarda mesmo se user deletado
    event      = models.CharField(max_length=20, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)   # UTC no banco

    class Meta:
        ordering = ['-timestamp']
        verbose_name        = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        indexes = [models.Index(fields=['-timestamp'])]

    def __str__(self):
        return f'{self.username} | {self.event} | {self.timestamp}'
