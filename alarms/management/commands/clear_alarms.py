import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Alarm


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Clear alarms from the past."

    def handle(self, *args, **options):
        alarms = Alarm.objects.filter(datetime_lte__lte=timezone.now())
        logger.info(f'{alarms.count()} Old alarms to be deleted')
        alarms.delete()
