# Generated manually to fix diet plan user association issue

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0020_alter_dietplan_breakfast_alter_dietplan_dinner_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dietplan',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
        ),
    ]
