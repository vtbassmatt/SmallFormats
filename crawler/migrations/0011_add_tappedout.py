# Generated by Django 4.1.3 on 2022-12-14 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0010_drop_follows'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawlrun',
            name='target',
            field=models.IntegerField(choices=[(0, 'Unknown/other'), (1, 'Archidekt'), (2, 'Moxfield'), (3, 'TappedOut')]),
        ),
    ]
