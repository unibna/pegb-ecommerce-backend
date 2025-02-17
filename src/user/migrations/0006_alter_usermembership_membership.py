# Generated by Django 3.2.25 on 2024-08-05 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0003_membership_rules'),
        ('user', '0005_usermembership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermembership',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='membership.membership'),
        ),
    ]
