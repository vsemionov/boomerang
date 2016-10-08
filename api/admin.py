from django.contrib import admin

# Register your models here.

from .models import Notebook, Note, Task

admin.site.register(Notebook)
admin.site.register(Note)
admin.site.register(Task)
