from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create all 7 initial FabricTrack users including admin'

    USERS = [
        {
            'username': 'admin',
            'password': 'admin@fabrictrack123',
            'first_name': 'Admin',
            'last_name': '',
            'person_type': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'cuttingmaster',
            'password': 'cutting@123',
            'first_name': 'Cutting',
            'last_name': 'Master',
            'person_type': 'P1',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'lakshay',
            'password': 'lakshay@123',
            'first_name': 'Lakshay',
            'last_name': '',
            'person_type': 'P2',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'rahul',
            'password': 'rahul@123',
            'first_name': 'Rahul',
            'last_name': '',
            'person_type': 'P3',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'miyaji',
            'password': 'miyaji@123',
            'first_name': 'Miya',
            'last_name': 'Ji',
            'person_type': 'P4',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'jobworker',
            'password': 'jobworker@123',
            'first_name': 'Job',
            'last_name': 'Worker',
            'person_type': 'P5',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'finishing',
            'password': 'finishing@123',
            'first_name': 'Finishing',
            'last_name': '',
            'person_type': 'P6',
            'is_staff': False,
            'is_superuser': False,
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write('Creating FabricTrack users...')
        created_count = 0
        skipped_count = 0

        for user_data in self.USERS:
            username = user_data['username']

            if User.objects.filter(username=username).exists():
                self.stdout.write(f'  [SKIP] {username} already exists')
                skipped_count += 1
                continue

            user = User.objects.create_user(
                username=username,
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser'],
            )

            UserProfile.objects.update_or_create(
                user=user,
                defaults={'person_type': user_data['person_type']}
            )

            role_label = 'ADMIN (superuser)' if user_data['is_superuser'] else user_data['person_type']
            self.stdout.write(
                f'  [OK] {username} | {role_label} | password: {user_data["password"]}'
            )
            created_count += 1

        self.stdout.write(f'Done: {created_count} created, {skipped_count} skipped.')
        self.stdout.write('')
        self.stdout.write('--- All Login Credentials ---')
        for u in self.USERS:
            self.stdout.write(f'  {u["username"]:15} | {u["password"]}')
