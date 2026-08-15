from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("chaves", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacao",
            name="observacoes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="movimentacao",
            name="data_hora_retirada",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
