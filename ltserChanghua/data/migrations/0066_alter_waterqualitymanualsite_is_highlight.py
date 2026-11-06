from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0065_waterquality_ammonianitrogen_waterquality_bod_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="waterqualitymanualsite",
            name="is_highlight",
            field=models.BooleanField(default=False, verbose_name="是否為河口水質監測點位"),
        ),
    ]
