from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.redirect_root, name='root'),
    path('manifest.json',  views.pwa_manifest,        name='pwa_manifest'),
    path('sw.js',          views.pwa_service_worker,  name='pwa_sw'),
    path('login/',     views.login_view,     name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reports/',   views.reports_view,   name='reports'),
    path('settings/',                views.settings_view,            name='settings'),
    path('settings/test-email/',     views.test_email_view,          name='test_email'),
    path('settings/openai-models/',  views.fetch_openai_models_view, name='fetch_openai_models'),
    path('settings/logs/',           views.logs_view,                name='logs'),
    path('settings/logs/export/csv/',  views.export_logs_csv,        name='export_logs_csv'),
    path('settings/logs/export/txt/',  views.export_logs_txt,        name='export_logs_txt'),
    path('settings/logs/export/xlsx/', views.export_logs_xlsx,       name='export_logs_xlsx'),
    path('logout/',    auth_views.LogoutView.as_view(), name='logout'),

    # Gestão de usuários
    path('users/',              views.users_list_view,  name='users_list'),
    path('users/novo/',         views.user_create_view, name='user_create'),
    path('users/<int:user_id>/editar/',  views.user_edit_view,   name='user_edit'),
    path('users/<int:user_id>/excluir/', views.user_delete_view, name='user_delete'),
]
