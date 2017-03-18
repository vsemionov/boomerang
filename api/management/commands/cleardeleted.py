import datetime
from collections import OrderedDict
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from api.models import Notebook, Note, Task


DELETED_EXPIRY_DAYS = getattr(settings, 'API_DELETED_EXPIRY_DAYS', 30)


class Command(BaseCommand):
    def handle(self, *args, **options):
        exectime = timezone.now()
        expiry = datetime.timedelta(days=DELETED_EXPIRY_DAYS)
        threshold = exectime - expiry

        classes = (Notebook, Note, Task)
        deletions = OrderedDict(((cls._meta.label, 0) for cls in classes))

        for cls in classes:
            deleted = cls.objects.filter(deleted=True)
            expired = deleted.filter(updated__lt=threshold)

            _, subdeletions = expired.delete()

            for cls in subdeletions:
                deletions[cls] += subdeletions[cls]

        for cls in deletions:
            print('%s: %d' % (cls, deletions[cls]))
