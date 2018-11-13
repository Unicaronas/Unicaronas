from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import F


class Command(BaseCommand):
    help = "Migrates usernames to the <id>@<university> format"

    def handle(self, *args, **options):
        # Get students that were not migrated
        users = User.objects.filter(student__isnull=False).exclude(username__endswith=F('student__university'))

        users = users.select_related('student')

        print('Updating', users.count(), 'users')
        for user in users:
            username = user.username
            university = user.student.university
            username = f"{username}@{university}"
            user.username = username
            user.save()

        print('Done')
