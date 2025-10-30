from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Book


class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "library_card_number",
            "first_name",
            "last_name",
            "email",
        ]


class BorrowerRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        "does_not_exist": 'User with pk "{pk_value}" does not exist.',
    }

    def to_representation(self, value):
        if value is None:
            return None
        borrower_model = get_user_model()

        if isinstance(value, borrower_model):
            borrower = value
        else:
            borrower_pk = getattr(value, "pk", value)
            borrower = borrower_model.objects.get(pk=borrower_pk)

        return BorrowerSerializer(borrower).data


class BookSerializer(serializers.ModelSerializer):
    borrowed_by = BorrowerRelatedField(queryset=get_user_model().objects.all(), allow_null=True, required=False)

    class Meta:
        model = Book
        fields = [
            "serial_number",
            "title",
            "author",
            "is_borrowed",
            "borrowed_at",
            "borrowed_by",
        ]
        read_only_fields = ["borrowed_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        is_borrowed = attrs.get("is_borrowed", getattr(self.instance, "is_borrowed", False))
        borrower = attrs.get("borrowed_by", getattr(self.instance, "borrowed_by", None))

        if is_borrowed:
            if not borrower:
                raise serializers.ValidationError("A borrower is required when the book is borrowed.")
            if not attrs.get("borrowed_at") and not getattr(self.instance, "borrowed_at", None):
                attrs["borrowed_at"] = timezone.now()
        else:
            attrs["borrowed_by"] = None
            attrs["borrowed_at"] = None

        return attrs

    def create(self, validated_data):
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=instance.pk)

            disallowed_fields = set(validated_data) - {"is_borrowed", "borrowed_by", "borrowed_at"}
            if disallowed_fields:
                raise serializers.ValidationError("Only the borrowing status of a book can be updated.")

            target_is_borrowed = validated_data.get("is_borrowed", book.is_borrowed)
            target_borrower = validated_data.get("borrowed_by", book.borrowed_by)
            target_borrowed_at = validated_data.get("borrowed_at", book.borrowed_at)

            # Update non-borrowing related fields. I wasn't convinced we should
            # allow updating other parameters; if we ever want the ability to update,
            # e.g., the title, uncomment this update and remove the guard above
            # + remove "http_method_names = ['get', 'post', 'delete', 'patch']"
            # from BookViewSet to allow PUT requests
            # normal circumstances I'd double-check with the PM during backlog
            # refinement :D).
            # for field, value in validated_data.items():
            #     if field not in {'is_borrowed', 'borrowed_by', 'borrowed_at'}:
            #         setattr(book, field, value)

            if target_is_borrowed:
                if not book.is_borrowed:
                    book.mark_borrowed(target_borrower, target_borrowed_at)
                elif target_borrower and target_borrower != book.borrowed_by:
                    raise serializers.ValidationError("This book has already been borrowed.")
                elif target_borrowed_at and target_borrowed_at != book.borrowed_at:
                    book.borrowed_at = target_borrowed_at
            else:
                if book.is_borrowed:
                    book.mark_returned()

            book.save()
            return book
