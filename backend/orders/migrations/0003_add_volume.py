from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_add_shelf_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='volume',
            field=models.DecimalField(decimal_places=3, default=0.01, help_text='Thể tích (m³)', max_digits=10),
        ),
    ]
