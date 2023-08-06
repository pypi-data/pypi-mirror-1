from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.commands import test

class Command(BaseCommand):
    def execute(self, *args, **kwargs):
        settings.TESTING = True
        settings.DEFAULT_FILE_STORAGE = "gypsy.storage.backends.memory.MemoryStorage"
        super(Command, self).execute(*args, **kwargs)

    def handle(self, *args, **kwargs):
        return test.Command().execute(*args, **kwargs)
