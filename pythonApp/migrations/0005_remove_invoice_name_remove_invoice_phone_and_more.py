# Generated by Django 4.2 on 2024-01-01 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pythonApp', '0004_alter_orders_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='name',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='total',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='town',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='kgs',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='packaging',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='price',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='rider',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='transport',
        ),
        migrations.RemoveField(
            model_name='invoicedetails',
            name='vat',
        ),
        migrations.AddField(
            model_name='invoice',
            name='customer_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='pythonApp.customer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoicedetails',
            name='orders_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pythonApp.orders'),
        ),
    ]
