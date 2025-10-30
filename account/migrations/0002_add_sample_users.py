from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_sample_users(apps, schema_editor):
    LibraryUser = apps.get_model("account", "LibraryUser")

    sample_users = [
        {
            "library_card_number": "123456",
            "defaults": {
                "first_name": "Anna",
                "last_name": "Nowak",
                "email": "anna.nowak@example.com",
                "password": make_password(None),
            },
        },
        {
            "library_card_number": "654321",
            "defaults": {
                "first_name": "Piotr",
                "last_name": "Kowalski",
                "email": "piotr.kowalski@example.com",
                "password": make_password(None),
            },
        },
        {
            "library_card_number": "111111",
            "defaults": {
                "first_name": "Maria",
                "last_name": "Wiśniewska",
                "email": "maria.wisniewska@example.com",
                "password": make_password(None),
            },
        },
        {
            "library_card_number": "000000",
            "defaults": {
                "first_name": "Jan",
                "last_name": "Zieliński",
                "email": "jan.zielinski@example.com",
                "is_staff": True,
                "is_superuser": True,
                "password": make_password("pass1234"),
            },
        },
    ]

    for user in sample_users:
        LibraryUser.objects.update_or_create(
            library_card_number=user["library_card_number"],
            defaults=user["defaults"],
        )


def remove_sample_users(apps, schema_editor):
    LibraryUser = apps.get_model("account", "LibraryUser")
    LibraryUser.objects.filter(library_card_number__in=["123456", "654321", "111111", "000000"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_sample_users, remove_sample_users),
    ]
