# Generated manually for initial migration
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies: list[str] = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "serial_number",
                    models.CharField(
                        max_length=6,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{6}$", "The serial number must contain exactly six digits."
                            )
                        ],
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                ("is_borrowed", models.BooleanField(default=False)),
                ("borrowed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "borrowed_by",
                    models.CharField(
                        blank=True,
                        max_length=6,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{6}$", "The library card number must contain exactly six digits."
                            )
                        ],
                    ),
                ),
            ],
            options={"ordering": ["serial_number"]},
        )
    ]
