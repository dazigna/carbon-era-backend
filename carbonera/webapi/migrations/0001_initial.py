# Generated by Django 3.2.9 on 2021-12-02 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Units',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('numerator', models.CharField(blank=True, max_length=64, null=True)),
                ('denominator', models.CharField(blank=True, max_length=64, null=True)),
            ],
        ),
    ]
