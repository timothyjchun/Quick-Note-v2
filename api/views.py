from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NoteSerializer, NoteContentFileSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from note.models import Note, NoteContent


class CreateNoteView(APIView):
    def post(self, request, *args, **kwargs):
        title = request.data["title"] if request.data["title"] else None
        password = request.data["password"] if request.data["password"] else None
        if not title:
            return Response({"message": "title is required"}, status=400)
        if Note.objects.filter(title__exact=title):
            return Response({"message": "title already exists"}, status=400)
        if not password:
            return Response({"message": "password is required"}, status=400)
        Note.objects.create(title=title, password=password)
        return Response(status=200)


class NoteIdNum(APIView):
    def get(self, request):
        obj_len = Note.objects.last().id
        return Response({"id": obj_len + 1}, status=200)


class GetRecentNotes(APIView):
    def get(self, request):
        obj = Note.objects.all()[::-1]
        serializer = NoteSerializer(obj, many=True)
        return Response(serializer.data, status=200)


class AuthenticateUserView(APIView):
    def post(self, request):
        req_password = request.data["password"]
        req_id = request.data["id"]
        note_obj_pass = Note.objects.get(id=req_id).password
        if req_password == note_obj_pass:
            return Response(status=200)
        else:
            return Response(status=401)


class FileHandleView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        data = request.data
        data["note"] = int(data["noteId"])
        del data["noteId"]
        # print(data)
        serializer = NoteContentFileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=200)
        else:
            print(serializer.errors)
            return Response(status=500)


class DeleteNotesView(APIView):
    def delete(self, request):
        note_id_to_delete = request.data["id"]
        note_to_delete = Note.objects.get(id=note_id_to_delete)
        note_to_delete.delete()  # maybe don't delete them for analytics
        return Response(status=200)
