from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

serial_validator = RegexValidator(r"^\d{6}$", "The serial number must contain exactly six digits.")
card_validator = RegexValidator(r"^\d{6}$", "The library card number must contain exactly six digits.")


class Book(models.Model):
    serial_number = models.CharField(max_length=6, unique=True, validators=[serial_validator])
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    is_borrowed = models.BooleanField(default=False)
    borrowed_at = models.DateTimeField(null=True, blank=True)
    borrowed_by = models.CharField(max_length=6, null=True, blank=True, validators=[card_validator])  # noqa

    class Meta:
        ordering = ["serial_number"]

    def mark_borrowed(self, borrower_id, borrowed_at=None):
        self.is_borrowed = True
        self.borrowed_by = borrower_id
        self.borrowed_at = borrowed_at or timezone.now()

    def mark_returned(self):
        self.is_borrowed = False
        self.borrowed_by = None
        self.borrowed_at = None

    def __str__(self):
        return f"{self.serial_number} - {self.title}"
