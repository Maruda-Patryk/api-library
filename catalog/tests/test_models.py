from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import Book


class BookModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            library_card_number="123456",
            first_name="Jan",
            last_name="Kowalski",
            password="testpass123",
        )

    def test_defaults(self):
        book = Book.objects.create(serial_number="000111", title="Quo Vadis", author="Henryk Sienkiewicz")

        self.assertFalse(book.is_borrowed)
        self.assertIsNone(book.borrowed_at)
        self.assertIsNone(book.borrowed_by)

    def test_str_representation(self):
        book = Book(serial_number="000222", title="Ferdydurke", author="Witold Gombrowicz")

        self.assertEqual(str(book), "000222 - Ferdydurke")

    def test_mark_borrowed_uses_timezone_now_by_default(self):
        book = Book.objects.create(serial_number="000333", title="Solaris", author="Stanislaw Lem")

        before_call = timezone.now() - timedelta(seconds=1)
        book.mark_borrowed(self.user)

        self.assertTrue(book.is_borrowed)
        self.assertEqual(book.borrowed_by, self.user)
        self.assertGreaterEqual(book.borrowed_at, before_call)

    def test_mark_borrowed_with_custom_timestamp(self):
        book = Book.objects.create(serial_number="000334", title="Solaris 2", author="Stanislaw Lem")
        custom_time = timezone.now() - timedelta(days=1)

        book.mark_borrowed(self.user, borrowed_at=custom_time)

        self.assertEqual(book.borrowed_at, custom_time)

    def test_mark_returned_clears_borrow_fields(self):
        book = Book.objects.create(
            serial_number="000444",
            title="The Manuscript Found in Saragossa",
            author="Jan Potocki",
            is_borrowed=True,
            borrowed_by=self.user,
            borrowed_at=timezone.now(),
        )

        book.mark_returned()

        self.assertFalse(book.is_borrowed)
        self.assertIsNone(book.borrowed_by)
        self.assertIsNone(book.borrowed_at)

    def test_serial_number_validator(self):
        book = Book(serial_number="abc123", title="Invalid Serial", author="Author")

        with self.assertRaises(ValidationError):
            book.full_clean()
