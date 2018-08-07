import uuid

from views.utils import APIBaseView, CreateView, ok_response
from views.serializers import ExampleSerializer


class ExampleView(CreateView):

    async def get(self, request, *args, **kwargs):



        return ok_response({})
