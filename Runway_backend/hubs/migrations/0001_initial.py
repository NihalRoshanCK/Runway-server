# Generated by Django 4.2.3 on 2023-10-11 13:51

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hub_name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('is_hotspot', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('number', models.BigIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hub_head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hubs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
