from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0002_alter_vehicle_options_remove_vehicle_capacity_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='plate_number',
            new_name='code',
        ),
    ]
