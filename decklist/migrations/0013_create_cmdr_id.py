# Generated by Django 4.1.3 on 2022-12-31 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decklist', '0012_add_card_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='commander',
            name='sfid',
            field=models.UUIDField(blank=True, null=True, verbose_name='SmallFormats ID'),
        ),
    ]
