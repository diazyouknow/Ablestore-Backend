# Generated by Django 3.1.4 on 2021-01-14 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
            options={
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=32)),
                ('password', models.CharField(max_length=256)),
                ('nickname', models.CharField(max_length=16)),
                ('code', models.CharField(max_length=16)),
                ('profile_image', models.URLField(default='https://i.pinimg.com/474x/34/c2/f9/34c2f984350ed23d1efa7094d7923c5a.jpg', max_length=512, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.country')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
