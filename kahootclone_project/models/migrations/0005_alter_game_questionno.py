# Generated by Django 3.2.1 on 2023-03-24 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0004_auto_20230323_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='questionNo',
            field=models.IntegerField(default=0, null=True),
        ),
    ]