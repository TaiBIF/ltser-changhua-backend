from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0062_iptcrabevent_iptcraboccurrenceextension"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crab",
            name="scientificName",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="crab",
            name="vernacularName",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
