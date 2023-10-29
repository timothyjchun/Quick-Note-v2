from rest_framework import serializers
from note.models import Note, NoteContent


import datetime

# This shouldn't be in the api module (app)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "color_name", "create_date"]
        # fields = ["id", "title", "color_name"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        note = Note.objects.get(id=ret["id"])
        ret["time_zone"] = "Asia/Seoul"
        ret["color_code"] = note.color_code
        ret["title_is_numeric"] = note.title_is_numeric
        ret["expire_date"] = note.expire_date
        return ret


class DateTimeSerializer(serializers.Serializer):
    create_date = serializers.DateTimeField()


class NoteContentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteContent
        fields = ["note", "file_content", "create_date"]
