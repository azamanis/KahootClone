# Generated by Django 3.2.1 on 2023-03-24 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0004_auto_20230323_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='correct',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='question',
            name='answerTime',
            field=models.IntegerField(blank=True, default=20),
        ),
    ]