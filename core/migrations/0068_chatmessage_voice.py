from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_add_chat_department_to_userprofile'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='chatmessage',
                    name='audio_data',
                    field=models.BinaryField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='chatmessage',
                    name='audio_duration',
                    field=models.PositiveIntegerField(default=0),
                ),
                migrations.AddField(
                    model_name='chatmessage',
                    name='audio_mime',
                    field=models.CharField(blank=True, max_length=100),
                ),
                migrations.AlterField(
                    model_name='chatmessage',
                    name='message_type',
                    field=models.CharField(
                        choices=[('text', 'Text'), ('task', 'Task card'), ('voice', 'Voice note')],
                        default='text',
                        max_length=10,
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
