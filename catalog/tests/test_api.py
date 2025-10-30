from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Book


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.list_url = reverse("book-list")
        User = get_user_model()
        self.user = User.objects.create_user(
            library_card_number="111222",
            first_name="Jan",
            last_name="Kowalski",
            password="testpass123",
        )

    def test_create_and_list_book(self):
        payload = {
            "serial_number": "123456",
            "title": "Pan Tadeusz",
            "author": "Adam Mickiewicz",
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertIsNone(list_response.data[0]["borrowed_by"])

    def test_borrow_and_return_book(self):
        book = Book.objects.create(serial_number="654321", title="Lalka", author="Boleslaw Prus")
        detail_url = reverse("book-detail", args=[book.serial_number])

        borrow_payload = {
            "is_borrowed": True,
            "borrowed_by": self.user.pk,
        }
        borrow_response = self.client.patch(detail_url, borrow_payload, format="json")
        self.assertEqual(borrow_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            borrow_response.data["borrowed_by"],
            {
                "library_card_number": self.user.library_card_number,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
            },
        )
        book.refresh_from_db()
        self.assertTrue(book.is_borrowed)
        self.assertEqual(book.borrowed_by, self.user)
        self.assertIsNotNone(book.borrowed_at)

        return_response = self.client.patch(detail_url, {"is_borrowed": False}, format="json")
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(return_response.data["borrowed_by"])
        book.refresh_from_db()
        self.assertFalse(book.is_borrowed)
        self.assertIsNone(book.borrowed_by)
        self.assertIsNone(book.borrowed_at)

    def test_borrow_race_condition_is_prevented(self):
        book = Book.objects.create(serial_number="777888", title="Quo Vadis", author="Henryk Sienkiewicz")
        detail_url = reverse("book-detail", args=[book.serial_number])

        User = get_user_model()
        first_user = User.objects.create_user(
            library_card_number="123123",
            first_name="Anna",
            last_name="Nowak",
            password="testpass123",
        )
        second_user = User.objects.create_user(
            library_card_number="999888",
            first_name="Piotr",
            last_name="Zielinski",
            password="testpass123",
        )

        first_borrow_payload = {
            "is_borrowed": True,
            "borrowed_by": first_user.pk,
        }
        second_borrow_payload = {
            "is_borrowed": True,
            "borrowed_by": second_user.pk,
        }

        first_response = self.client.patch(detail_url, first_borrow_payload, format="json")
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.patch(detail_url, second_borrow_payload, format="json")
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been borrowed", str(second_response.data))

        book.refresh_from_db()
        self.assertEqual(book.borrowed_by, first_user)

    def test_borrow_with_nonexistent_user_returns_clear_message(self):
        book = Book.objects.create(serial_number="555666", title="Ogniem i Mieczem", author="Henryk Sienkiewicz")
        detail_url = reverse("book-detail", args=[book.serial_number])

        response = self.client.patch(
            detail_url,
            {"is_borrowed": True, "borrowed_by": 987654},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["borrowed_by"],
            ['User with pk "987654" does not exist.'],
        )
