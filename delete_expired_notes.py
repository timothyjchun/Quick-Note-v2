import os
import django
import datetime
import pytz

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

# Initialize Django
django.setup()


from note.models import Note


# today = datetime.date.today()
"""local 시간에 맞는건 아니지만, 그냥 UTC로 해도 똑같이 동작하기에 불필요하게 또 변환하지 않는다."""
now = pytz.timezone("UTC").localize(datetime.datetime.now())


for note in Note.objects.all():
    if (
        # note.create_date + datetime.timedelta(days=1)
        # < now
        note.create_date + datetime.timedelta(seconds=1)
        < now
    ):  # 이렇게 말고 Note.expire_date를 쓰자
        note.delete()  # analytics를 위해서라면 지우지는 말자.
