from django.db import models
import random
from datetime import timedelta

# Create your models here.


color_data = {
    "red": "#FF0000",
    "dark_orange": "#FF6100",
    "orange": "#FF9000",
    "green": "#00A300",
    "blue": "#0085FF",
    "dark_blue": "#0000FF",
    "purple": "#9B00FF",
    "pink": "#FF00A2",
}
color_options = list(color_data.keys()) + [
    "pink",
    "blue",
    "blue",
    "blue",
    "purple",
    "purple",
    "pink",
    "pink",
]


class Note(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    password = models.CharField(default="qwertyasdf", max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    color_name = models.CharField(
        max_length=40, null=False, default=lambda: random.choice(color_options)
    )

    @property
    def color_code(self):
        return color_data[self.color_name]

    @property
    def thumbnail(self):
        return self.title[0]

    @property
    def title_is_numeric(self):
        return self.title.isnumeric()

    @property
    def expire_date(self):
        one_day = timedelta(days=1)
        return self.create_date + one_day

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.id


class NoteContent(models.Model):
    note = models.ForeignKey(Note, models.CASCADE)
    text_content = models.TextField(null=True, blank=True)
    file_content = models.FileField(null=True, blank=True, upload_to="files/")
    create_date = models.DateTimeField(auto_now_add=True)

    @property
    def calculate_content_container(self):
        if self.text_content:
            rows = self.text_content.count("\n")
            columns = len(
                sorted(self.text_content.split("\n"), key=lambda x: len(x))[-1]
            )
            return {"rows": rows, "columns": columns}
