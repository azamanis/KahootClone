# Generated by Django 3.2.1 on 2023-04-02 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0009_alter_game_countdowntime'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participant',
            options={'ordering': ['-points']},
        ),
    ]
