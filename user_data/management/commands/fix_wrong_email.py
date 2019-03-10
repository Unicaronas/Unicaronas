from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from user_data.models import UNIVERSITY_CHOICES

u_choices = '; '.join([a + ' for ' + b for a, b in UNIVERSITY_CHOICES])


class Command(BaseCommand):
    help = "Fix wrong email typed by users."

    def add_arguments(self, parser):
        parser.add_argument('user_id', help='ID of the user')
        parser.add_argument('university', help=f'Univeristy of the user. Options are: {u_choices}')
        parser.add_argument('new_email', help='New email')

    def handle(self, *args, **options):
        user_id = options['user_id']
        university = options['university']
        new_email = options['new_email']
        print('Getting user')
        user = User.objects.filter(student__university_id=user_id, student__university=university)
        if not user.exists():
            print('User was not found')
            exit()
        if not user.count() == 1:
            print('More than one user found')
            exit()
        user = user.first()
        print('User found', user)

        print('Getting primary email')
        primary = EmailAddress.objects.get_primary(user)
        if not primary:
            primary('User does not have a primary email')
            exit()
        print('Primary email found', primary)
        primary.email = new_email
        primary.save()
        print('New email set as primary')

        print('Setting university email')
        student = user.student
        student.university_email = new_email
        student.save()

        print('Done')
