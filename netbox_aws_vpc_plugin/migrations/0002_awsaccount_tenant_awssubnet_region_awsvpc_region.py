# Generated by Django 5.1.8 on 2025-04-21 04:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0200_populate_mac_addresses"),
        ("netbox_aws_vpc_plugin", "0001_initial"),
        ("tenancy", "0017_natural_ordering"),
    ]

    operations = [
        migrations.AddField(
            model_name="awsaccount",
            name="tenant",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="tenancy.tenant"
            ),
        ),
        migrations.AddField(
            model_name="awssubnet",
            name="region",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="dcim.region"
            ),
        ),
        migrations.AddField(
            model_name="awsvpc",
            name="region",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="dcim.region"
            ),
        ),
    ]
