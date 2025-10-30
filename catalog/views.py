from rest_framework import mixins, viewsets

from .models import Book
from .serializers import BookSerializer


class BookViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    # Normally, ModelViewSet could be used here since it combines all these mixins,
    # but it also includes the Retrieve action (GET for a single object),
    # which was not mentioned in the task description.
    queryset = Book.objects.all()
    http_method_names = ["get", "post", "delete", "patch"]
    serializer_class = BookSerializer
    lookup_field = "serial_number"
