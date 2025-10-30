from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Book


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.list_url = reverse("book-list")

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

    def test_borrow_and_return_book(self):
        book = Book.objects.create(serial_number="654321", title="Lalka", author="Boleslaw Prus")
        detail_url = reverse("book-detail", args=[book.serial_number])

        borrow_payload = {
            "is_borrowed": True,
            "borrowed_by": "111222",
        }
        borrow_response = self.client.patch(detail_url, borrow_payload, format="json")
        self.assertEqual(borrow_response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertTrue(book.is_borrowed)
        self.assertEqual(book.borrowed_by, "111222")
        self.assertIsNotNone(book.borrowed_at)

        return_response = self.client.patch(detail_url, {"is_borrowed": False}, format="json")
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertFalse(book.is_borrowed)
        self.assertIsNone(book.borrowed_by)
        self.assertIsNone(book.borrowed_at)

    def test_borrow_race_condition_is_prevented(self):
        book = Book.objects.create(serial_number="777888", title="Quo Vadis", author="Henryk Sienkiewicz")
        detail_url = reverse("book-detail", args=[book.serial_number])

        first_borrow_payload = {
            "is_borrowed": True,
            "borrowed_by": "123123",
        }
        second_borrow_payload = {
            "is_borrowed": True,
            "borrowed_by": "999888",
        }

        first_response = self.client.patch(detail_url, first_borrow_payload, format="json")
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.patch(detail_url, second_borrow_payload, format="json")
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been borrowed", str(second_response.data))

        book.refresh_from_db()
        self.assertEqual(book.borrowed_by, "123123")
