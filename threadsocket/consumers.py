import json
import re
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from django.utils.text import get_valid_filename

from note.models import Note, NoteContent

from api.serializers import DateTimeSerializer


class ThreadConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.thread_obj = None

    async def connect(self):
        self.thread_name = self.scope["url_route"]["kwargs"]["note_title"]
        self.thread_group_name = f"thread_{self.thread_name}"

        # Join room group
        await self.channel_layer.group_add(self.thread_group_name, self.channel_name)

        await self.accept()

        res = await self.get_thread_data_or_new(self.thread_name)
        if res:
            for data in res:
                await self.send(text_data=json.dumps({"data": data}))

    @database_sync_to_async
    def get_thread_data_or_new(self, thread_name):
        thread = Note.objects.filter(title__exact=thread_name)
        if len(thread) == 0:  # new
            new_thread = Note.objects.create(title=thread_name)
            self.thread_obj = new_thread
            return 0
        else:  # existing
            self.thread_obj = thread[0]
            data = []
            thread_content = self.thread_obj.notecontent_set.all()
            for content in thread_content:
                data_snippet = {}
                if content.text_content:
                    data_snippet["create_date"] = DateTimeSerializer(content).data[
                        "create_date"
                    ]
                    data_snippet["content"] = content.text_content.split("\n")
                    data_snippet["row_column"] = content.calculate_content_container

                elif content.file_content:
                    # data.append(content.file_content)
                    content_name = content.file_content.__str__().split("files/")[-1]
                    data_snippet["content"] = [content_name]
                    data_snippet["create_date"] = DateTimeSerializer(content).data[
                        "create_date"
                    ]
                    data_snippet["row_column"] = {
                        "rows": 0,
                        "columns": len(content_name),
                    }
                    data_snippet["type"] = "file"
                data.append(data_snippet)

            return data

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.thread_name, self.channel_name)
        print("Successfully left room")

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get("type", None) == "file":
            # if " " in text_data_json["data"]:  # 파일 이름에 공백이 들어가있는지 확인하기
            #     text_data_json["data"] = text_data_json["data"].replace(" ", "_")
            text_data_json["data"] = get_valid_filename(text_data_json["data"])

            file_filter_name = text_data_json["data"].rsplit(".", 1)[
                0
            ]  # 검색할때 확장자 없이 파일 이름만 검색
            file_obj = await self.process_file_data(file_filter_name)
            file_obj_name = file_obj.file_content.__str__().split("files/")[-1]
            # print(file_obj_name)
            # print(type(file_obj_name))

            data_send = {"content": [file_obj_name]}
            data_send["create_date"] = DateTimeSerializer(file_obj).data["create_date"]
            data_send["row_column"] = {"rows": 0, "columns": len(file_obj_name)}
            data_send["type"] = "file"

            await self.channel_layer.group_send(
                self.thread_group_name,
                {
                    "type": "thread.data",
                    "data": data_send,
                },
            )

        else:
            data = text_data_json["data"]
            # Send message to room group
            data_obj = await self.process_thread_data(data)
            data_send = {"content": data.split("\n")}
            data_send["create_date"] = DateTimeSerializer(data_obj).data["create_date"]
            data_send["row_column"] = data_obj.calculate_content_container

            await self.channel_layer.group_send(
                self.thread_group_name,
                {
                    "type": "thread.data",
                    "data": data_send,
                },  # "type" being the method, "message" being the argument
            )

    # Receive message from room group
    async def thread_data(self, event):
        event_data = event["data"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"data": event_data}))

    @database_sync_to_async
    def process_thread_data(self, data):
        n = NoteContent(note=self.thread_obj, text_content=data)
        n.save()
        return n

    @database_sync_to_async
    def process_file_data(self, file_name_snippet):
        # print(f"============file_name_snippet : {file_name_snippet}============")
        file_name_snippet = get_valid_filename(file_name_snippet)

        note_content_candidates = NoteContent.objects.filter(
            file_content__contains=file_name_snippet
        )

        # print(len(note_content_candidates))
        note_content_target = note_content_candidates[len(note_content_candidates) - 1]
        return note_content_target
