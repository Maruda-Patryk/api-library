from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

card_validator = RegexValidator(r"^\d{6}$", "The library card number must contain exactly six digits.")


class LibraryUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, library_card_number, password, **extra_fields):
        if not library_card_number:
            raise ValueError("The library card number must be set.")

        email = extra_fields.get("email")
        extra_fields["email"] = self.normalize_email(email) if email else ""

        user = self.model(library_card_number=library_card_number, **extra_fields)
        user.set_password(password) if password else user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, library_card_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(library_card_number, password, **extra_fields)

    def create_superuser(self, library_card_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(library_card_number, password, **extra_fields)


class LibraryUser(AbstractBaseUser, PermissionsMixin):
    library_card_number = models.CharField(
        primary_key=True,
        max_length=6,
        validators=[card_validator],
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active.",
    )
    date_joined = models.DateTimeField(default=timezone.now)

    objects = LibraryUserManager()

    USERNAME_FIELD = "library_card_number"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["library_card_number"]

    def __str__(self):
        return self.library_card_number
