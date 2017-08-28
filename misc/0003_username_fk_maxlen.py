from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_trigram_ext'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE api_notebook ALTER COLUMN user_id TYPE VARCHAR(150);',
            reverse_sql='ALTER TABLE api_notebook ALTER COLUMN user_id TYPE VARCHAR(30);'
        ),
        migrations.RunSQL(
            sql='ALTER TABLE api_task ALTER COLUMN user_id TYPE VARCHAR(150);',
            reverse_sql='ALTER TABLE api_task ALTER COLUMN user_id TYPE VARCHAR(30);'
        ),
    ]
