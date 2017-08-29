import datetime
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from rest_offline.models import TrackedModel


class Command(BaseCommand):
    def handle(self, *args, **options):
        expiry_days = getattr(settings, 'REST_OFFLINE', None) and settings.REST_OFFLINE.get('DELETED_EXPIRY_DAYS')
        if not expiry_days:
            return

        threshold = timezone.now() - datetime.timedelta(days=expiry_days)

        classes = TrackedModel.__subclasses__()
        deletions = OrderedDict((cls._meta.label, 0) for cls in classes \
                                if cls._meta.abstract is False and cls._meta.proxy is False)

        for cls in classes:
            deleted = cls.objects.filter(deleted=True)
            expired = deleted.filter(updated__lt=threshold)

            _, subdeletions = expired.delete()

            for delcls in subdeletions:
                deletions[delcls] += subdeletions[delcls]

        for cls in deletions:
            print('%s: %d' % (cls, deletions[cls]))
