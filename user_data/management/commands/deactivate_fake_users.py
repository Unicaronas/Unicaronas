import re
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from user_data.mailing import fake_user_warn_email


def real_university_id(email):
    u = re.search(r'[a-z]?(\d+)@[a-z]*[.]?unicamp.br', email, re.IGNORECASE)
    if not u:
        return False
    return u.group(1)


def is_fake_id(data):
    u_id = real_university_id(data[2])
    return data[1] != u_id if u_id else False


def deactivate_fake_users(commit=False, return_mistyped=False):
    user_list = User.objects.filter(student__university='unicamp', emailaddress__verified=True).values_list('id', 'student__university_id', 'student__university_email')
    fake_users = []
    mistyped_users = []
    for fake_user in User.objects.filter(pk__in=map(lambda x: x[0], filter(is_fake_id, user_list))).prefetch_related('student'):
        try:
            fake_users.append({
                'fake': fake_user,
                'real': User.objects.get(student__university_id=real_university_id(fake_user.student.university_email))
            })
        except User.DoesNotExist:
            mistyped_users.append(fake_user)
    print(f'Desativando {len(fake_users)} usuários falsos (commit: {commit})')
    for user in fake_users:
        real = user['real']
        fake = user['fake']
        if commit:
            fake_user_warn_email(fake)
            real.email = fake.student.university_email
            real.is_active = False
            real.save()
            fake.delete()
    print(f'Pronto')
    if return_mistyped:
        return mistyped_users


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            help="Commit or not the changes",
            action='store_true'
        )

    def handle(self, *args, **options):
        return deactivate_fake_users(options['commit'])
