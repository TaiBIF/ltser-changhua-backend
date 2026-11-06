from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0063_alter_crab_scientificname_alter_crab_vernacularname"),
    ]

    operations = [
        migrations.AddField(
            model_name="waterqualitymanualsite",
            name="is_highlight",
            field=models.BooleanField(default=False, verbose_name="前端重點標示"),
        ),
    ]
