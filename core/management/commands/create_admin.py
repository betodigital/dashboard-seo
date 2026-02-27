from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Cria o usuário admin padrão com senha 123456'

    def handle(self, *args, **options):
        username = 'admin'
        password = '123456'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Usuário "{username}" já existe. Nada foi alterado.'
            ))
        else:
            User.objects.create_superuser(
                username=username,
                email='admin@example.com',
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superusuário "{username}" criado com sucesso!'
            ))
