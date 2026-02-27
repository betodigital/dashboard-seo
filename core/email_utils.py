import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.template.loader import render_to_string

from .config_utils import get_all_configs


SMTP_KEYS = [
    'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password',
    'smtp_use_tls', 'smtp_use_ssl', 'email_from', 'email_from_name',
]


def _get_smtp_config():
    return get_all_configs(SMTP_KEYS)


def send_html_email(to_email, subject, html_body):
    """
    Send an HTML email using SMTP settings stored in SystemConfig.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    cfg = _get_smtp_config()

    host     = cfg.get('smtp_host', '').strip()
    port_str = cfg.get('smtp_port', '587').strip()
    user     = cfg.get('smtp_user', '').strip()
    password = cfg.get('smtp_password', '')
    use_tls  = cfg.get('smtp_use_tls', '1') == '1'
    use_ssl  = cfg.get('smtp_use_ssl', '0') == '1'
    from_addr = cfg.get('email_from', user).strip() or user
    from_name = cfg.get('email_from_name', 'MyApp').strip()

    if not host or not user or not password:
        return False, 'SMTP nao configurado. Preencha as configuracoes de e-mail.'

    try:
        port = int(port_str)
    except (ValueError, TypeError):
        port = 587

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'{from_name} <{from_addr}>'
    msg['To']      = to_email
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context) as server:
                server.login(user, password)
                server.sendmail(from_addr, [to_email], msg.as_bytes())
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                if use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.ehlo()
                server.login(user, password)
                server.sendmail(from_addr, [to_email], msg.as_bytes())
        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, 'Falha de autenticacao SMTP. Verifique usuario e senha.'
    except smtplib.SMTPConnectError:
        return False, f'Nao foi possivel conectar ao servidor {host}:{port}.'
    except smtplib.SMTPException as e:
        return False, f'Erro SMTP: {e}'
    except OSError as e:
        return False, f'Erro de rede: {e}'
    except Exception as e:
        return False, f'Erro inesperado: {e}'


def send_welcome_email(user):
    """
    Send a beautiful welcome email to a newly created user.
    Returns (True, None) or (False, error_message).
    """
    to_email = user.email
    if not to_email:
        return False, 'Usuario nao possui e-mail cadastrado.'

    try:
        profile = user.profile
    except Exception:
        profile = None

    display_name = (profile.get_display_name() if profile else None) or user.username

    permissions_list = []
    if user.is_superuser:
        permissions_list = ['Dashboard', 'Relatorios', 'Configuracoes', 'Usuarios']
    elif profile:
        if profile.can_view_dashboard: permissions_list.append('Dashboard')
        if profile.can_view_reports:   permissions_list.append('Relatorios')
        if profile.can_view_settings:  permissions_list.append('Configuracoes')
        if profile.can_view_users:     permissions_list.append('Usuarios')

    from .config_utils import get_config
    app_url = get_config('app_url', 'http://localhost:8000')

    context = {
        'username':         user.username,
        'display_name':     display_name,
        'app_url':          app_url,
        'permissions_list': permissions_list,
    }

    html_body = render_to_string('emails/welcome.html', context)
    return send_html_email(to_email, 'Bem-vindo ao MyApp!', html_body)


def send_lockout_alert(ip_address, username, user_agent=''):
    """
    Envia alerta de bloqueio para todos os superusuários com e-mail cadastrado.
    Chamado quando um IP é bloqueado após 3 tentativas erradas.
    """
    from django.contrib.auth.models import User
    from .config_utils import get_config
    import datetime

    system_name = get_config('system_name', 'MyApp') or 'MyApp'
    app_url = get_config('app_url', 'http://localhost:8000')

    # Busca todos os superusuários com e-mail
    admins = User.objects.filter(is_superuser=True, is_active=True).exclude(email='')
    if not admins.exists():
        return

    now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    html_body = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:40px 20px;">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#13131a;border-radius:16px;overflow:hidden;border:1px solid #2a2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#dc2626,#ef4444);padding:32px;text-align:center;">
            <p style="margin:0;font-size:28px;font-weight:700;color:#fff;">{system_name}</p>
            <p style="margin:8px 0 0;color:rgba(255,255,255,.85);font-size:15px;font-weight:600;">
              &#x26A0; Alerta de Seguranca — IP Bloqueado
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 32px;color:#e2e8f0;">
            <p style="font-size:18px;font-weight:600;margin:0 0 16px;color:#fff;">
              Um IP foi bloqueado por excesso de tentativas de login
            </p>
            <p style="margin:0 0 24px;color:#94a3b8;line-height:1.7;">
              O sistema detectou <strong style="color:#ef4444;">3 tentativas erradas de senha</strong>
              consecutivas e bloqueou o acesso por <strong style="color:#fff;">1 hora</strong>.
            </p>

            <div style="background:#1a1a2e;border-radius:10px;padding:20px 24px;border-left:4px solid #ef4444;margin-bottom:20px;">
              <table cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td style="color:#94a3b8;font-size:13px;padding:4px 0;width:140px;">IP bloqueado:</td>
                  <td style="color:#f87171;font-size:13px;font-weight:700;font-family:monospace;">{ip_address}</td>
                </tr>
                <tr>
                  <td style="color:#94a3b8;font-size:13px;padding:4px 0;">Usuário tentado:</td>
                  <td style="color:#fff;font-size:13px;font-weight:600;">{username or '(desconhecido)'}</td>
                </tr>
                <tr>
                  <td style="color:#94a3b8;font-size:13px;padding:4px 0;">Data/Hora (SP):</td>
                  <td style="color:#fff;font-size:13px;">{now_str}</td>
                </tr>
                <tr>
                  <td style="color:#94a3b8;font-size:13px;padding:4px 0;vertical-align:top;">User Agent:</td>
                  <td style="color:#64748b;font-size:11px;word-break:break-all;">{(user_agent or 'N/A')[:200]}</td>
                </tr>
              </table>
            </div>

            <div style="background:#111827;border-radius:8px;padding:14px 18px;border:1px solid #374151;">
              <p style="margin:0;color:#9ca3af;font-size:13px;line-height:1.6;">
                O IP ficara bloqueado por <strong style="color:#fff;">1 hora</strong> automaticamente.
                Se necessario, voce pode desbloquear manualmente no
                <a href="{app_url}/admin/axes/accessattempt/" style="color:#a78bfa;">painel de administracao</a>.
              </p>
            </div>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 32px 28px;text-align:center;color:#475569;font-size:12px;">
            Alerta automatico de seguranca — {system_name} — nao responda.
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    subject = f'[{system_name}] Alerta: IP {ip_address} bloqueado por tentativas de login'
    for admin in admins:
        try:
            send_html_email(admin.email, subject, html_body)
        except Exception:
            pass


def send_test_email(to_email):
    """Send a simple test email to verify SMTP settings."""
    html_body = """
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:40px 20px;">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#13131a;border-radius:16px;overflow:hidden;border:1px solid #2a2a3a;">
        <tr>
          <td style="background:linear-gradient(135deg,#6c63ff,#a78bfa);padding:32px;text-align:center;">
            <p style="margin:0;font-size:28px;font-weight:700;color:#fff;">MyApp</p>
            <p style="margin:8px 0 0;color:rgba(255,255,255,.8);font-size:14px;">Teste de Configuracao SMTP</p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 32px;color:#e2e8f0;">
            <p style="font-size:20px;font-weight:600;margin:0 0 16px;color:#fff;">
              Configuracao bem-sucedida!
            </p>
            <p style="margin:0 0 24px;color:#94a3b8;line-height:1.7;">
              Este e-mail confirma que as suas configuracoes de SMTP estao corretas
              e o envio de e-mails esta funcionando normalmente.
            </p>
            <div style="background:#1e1e2e;border-radius:10px;padding:16px 20px;border-left:3px solid #6c63ff;">
              <p style="margin:0;color:#a78bfa;font-size:13px;">
                Provedor SMTP configurado com sucesso. Os e-mails de boas-vindas
                serao enviados automaticamente ao criar novos usuarios.
              </p>
            </div>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 32px 28px;text-align:center;color:#475569;font-size:12px;">
            E-mail enviado automaticamente pelo MyApp — nao responda.
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return send_html_email(to_email, 'Teste de SMTP — MyApp', html_body)
