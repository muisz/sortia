# Generated by Django 4.2.6 on 2023-10-29 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('expired_at', models.DateTimeField()),
                ('used_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
