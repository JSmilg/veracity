import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0006_claim_is_transfer_negative'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceClub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfermarkt_id', models.IntegerField(db_index=True, unique=True)),
                ('name', models.CharField(db_index=True, max_length=300)),
                ('slug', models.SlugField(blank=True, max_length=300)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('competition', models.CharField(blank=True, max_length=200)),
                ('logo_url', models.URLField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Reference Club',
                'verbose_name_plural': 'Reference Clubs',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['name'], name='claims_refe_name_club_idx'),
                    models.Index(fields=['country'], name='claims_refe_country_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ReferencePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfermarkt_id', models.IntegerField(db_index=True, unique=True)),
                ('name', models.CharField(db_index=True, max_length=300)),
                ('slug', models.SlugField(blank=True, max_length=300)),
                ('current_club_name', models.CharField(blank=True, help_text='Denormalised club name for quick lookups', max_length=300)),
                ('on_loan_from_club_name', models.CharField(blank=True, max_length=300)),
                ('position', models.CharField(blank=True, max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('citizenship', models.CharField(blank=True, max_length=200)),
                ('contract_expires', models.DateField(blank=True, null=True)),
                ('image_url', models.URLField(blank=True, max_length=500)),
                ('is_manager', models.BooleanField(default=False, help_text='True if this person is known to be a manager, not a player')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_club', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='players', to='claims.referenceclub')),
                ('on_loan_from_club', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loaned_out_players', to='claims.referenceclub')),
            ],
            options={
                'verbose_name': 'Reference Player',
                'verbose_name_plural': 'Reference Players',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['name'], name='claims_refe_name_player_idx'),
                    models.Index(fields=['current_club_name'], name='claims_refe_club_name_idx'),
                    models.Index(fields=['position'], name='claims_refe_position_idx'),
                ],
            },
        ),
    ]
