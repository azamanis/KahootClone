# Generated by Django 3.2.1 on 2023-04-02 16:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0010_alter_participant_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='countdownTime',
            field=models.IntegerField(default=5, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='question',
            name='answerTime',
            field=models.IntegerField(blank=True, default=20, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
