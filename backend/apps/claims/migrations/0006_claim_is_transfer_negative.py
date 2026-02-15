from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0005_alter_claim_article_url_alter_claim_from_club_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='is_transfer_negative',
            field=models.BooleanField(
                default=False,
                db_index=True,
                help_text='Claim indicates deal will NOT happen (extension, rejection, staying)',
            ),
        ),
    ]
