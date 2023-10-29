from django.contrib import admin
from .models import Note, NoteContent

# Register your models here.

admin.site.register(Note)
admin.site.register(NoteContent)
