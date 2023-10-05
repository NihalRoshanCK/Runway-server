# Generated by Django 4.2.3 on 2023-09-28 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hubs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auths', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to='media/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socketSystem.notificationcontent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')], max_length=10)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='hubs.hub')),
                ('media', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='socketSystem.messagemedia')),
                ('seen_by_staff', models.ManyToManyField(blank=True, to='auths.staff')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
