from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.models import User
from django.dispatch import receiver
from axes.signals import user_locked_out
from .models import UserProfile


# ── Registros de log de acesso ─────────────────────────────────────
@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    try:
        from .log_utils import record_login_ok
        record_login_ok(request, user)
    except Exception:
        pass


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    if user and user.is_authenticated:
        try:
            from .log_utils import record_logout
            record_logout(request, user)
        except Exception:
            pass


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    try:
        from .log_utils import record_login_fail
        record_login_fail(request, credentials.get('username', ''))
    except Exception:
        pass


# ── Bloqueio de IP por excesso de tentativas ───────────────────────
@receiver(user_locked_out)
def on_user_locked_out(sender, request, username, ip_address, **kwargs):
    """Disparado pelo django-axes quando um IP é bloqueado."""
    try:
        from .log_utils import record_lockout, get_client_ip
        ip = ip_address or get_client_ip(request)
        record_lockout(request, username)
    except Exception:
        pass

    # Envia e-mail de alerta para todos os admins (falha silenciosa)
    try:
        from .email_utils import send_lockout_alert
        from .log_utils import get_client_ip
        ip = ip_address or get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        send_lockout_alert(ip, username, user_agent)
    except Exception:
        pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria um UserProfile automaticamente ao criar um usuario e envia e-mail de boas-vindas."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        # Envia e-mail de boas-vindas (falha silenciosa — nunca bloqueia o cadastro)
        if instance.email:
            try:
                from .email_utils import send_welcome_email
                send_welcome_email(instance)
            except Exception:
                pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
