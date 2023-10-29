from django.urls import path
from .views import (
    CreateNoteView,
    NoteIdNum,
    GetRecentNotes,
    AuthenticateUserView,
    FileHandleView,
    DeleteNotesView,
)


urlpatterns = [
    path("create_note/", CreateNoteView.as_view()),
    path("get_id_num/", NoteIdNum.as_view()),
    path("get_recent_notes/", GetRecentNotes.as_view()),
    path("authenticate_user/", AuthenticateUserView.as_view()),
    path("file_handle/", FileHandleView.as_view()),
    path("delete_note/", DeleteNotesView.as_view()),
]
