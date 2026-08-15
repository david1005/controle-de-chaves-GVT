import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chaves", "0002_movimentacao_observacoes_alter_data_hora_retirada"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pessoa",
            name="foto",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="fotos_pessoas/",
                validators=[django.core.validators.FileExtensionValidator(
                    allowed_extensions=["jpg", "jpeg", "png", "webp"],
                )],
            ),
        ),
    ]
