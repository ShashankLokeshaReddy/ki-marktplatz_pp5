from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jobID', models.CharField(max_length=140, null=True)),
                ('resourceId', models.CharField(max_length=140, null=True)),
                ('partID', models.CharField(max_length=140, null=True)),
                ('jobInputDate', models.DateTimeField(null=True)),
                ('deadlineDate', models.DateTimeField(null=True)),
                ('productionStart', models.DateTimeField(null=True)),
                ('productionEnd', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ('jobID',),
            },
        ),
    ]

