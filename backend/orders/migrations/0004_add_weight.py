from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_add_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=1.0, help_text='Khối lượng (kg)', max_digits=10),
        ),
    ]
