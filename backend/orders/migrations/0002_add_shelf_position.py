from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shelf_position',
            field=models.CharField(blank=True, help_text='Format: SHELF-ROW-COL-LEVEL', max_length=50, null=True),
        ),
    ]
