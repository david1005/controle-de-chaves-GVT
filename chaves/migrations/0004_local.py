from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chaves", "0003_alter_pessoa_foto"),
    ]

    operations = [
        migrations.CreateModel(
            name="Local",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name": "Local",
                "verbose_name_plural": "Locais",
                "ordering": ["nome"],
            },
        ),
    ]
