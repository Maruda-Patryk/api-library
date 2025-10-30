from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

serial_validator = RegexValidator(r"^\d{6}$", "The serial number must contain exactly six digits.")


class Book(models.Model):
    serial_number = models.CharField(max_length=6, unique=True, validators=[serial_validator])
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    is_borrowed = models.BooleanField(default=False)
    borrowed_at = models.DateTimeField(null=True, blank=True)
    borrowed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="borrowed_books",
    )

    class Meta:
        ordering = ["serial_number"]

    def mark_borrowed(self, borrower, borrowed_at=None):
        self.is_borrowed = True
        self.borrowed_by = borrower
        self.borrowed_at = borrowed_at or timezone.now()

    def mark_returned(self):
        self.is_borrowed = False
        self.borrowed_by = None
        self.borrowed_at = None

    def __str__(self):
        return f"{self.serial_number} - {self.title}"
