# Generated by Django 3.2.9 on 2022-01-12 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='webapi.category', verbose_name='parent')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, null=True)),
                ('numerator', models.CharField(max_length=64, null=True)),
                ('denominator', models.CharField(max_length=64, null=True)),
                ('quantity', models.CharField(max_length=64, null=True)),
                ('attribute', models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_fr', models.TextField(null=True)),
                ('name_en', models.TextField(null=True)),
                ('attribute_fr', models.TextField(null=True)),
                ('attribute_en', models.TextField(null=True)),
                ('category_str', models.TextField(null=True)),
                ('tag_fr', models.TextField(null=True)),
                ('tag_en', models.TextField(null=True)),
                ('unit_str', models.TextField(null=True)),
                ('confidence', models.IntegerField(null=True)),
                ('total_poste', models.FloatField(null=True)),
                ('co2f', models.FloatField(null=True)),
                ('ch4f', models.FloatField(null=True)),
                ('ch4b', models.FloatField(null=True)),
                ('n2o', models.FloatField(null=True)),
                ('co2b', models.FloatField(null=True)),
                ('other_ghg', models.FloatField(null=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapi.category')),
                ('unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapi.unit')),
            ],
        ),
    ]
