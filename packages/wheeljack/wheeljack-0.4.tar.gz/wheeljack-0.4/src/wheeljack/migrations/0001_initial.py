from south.db import db
from django.db import models
from wheeljack.models import supported_repositories, states

class Migration:

    def forwards(self):
        # Model 'Project'
        db.create_table('wheeljack_project', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField(max_length=256)),
            ('build_cmd', models.CharField(max_length=256)),
            ('repository', models.CharField(max_length=256)),
            ('vcs', models.CharField(max_length=8, choices=supported_repositories)),
            ('watch_list', models.TextField()),
            ('last_modified', models.DateTimeField(auto_now=True)),
        ))
        # Mock Models
        Project = db.mock_model(model_name='Project', db_table='wheeljack_project', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        # Model 'BuildLog'
        db.create_table('wheeljack_buildlog', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(Project)),
            ('revision', models.CharField(max_length=512)),
            ('output', models.TextField()),
            ('state', models.CharField(max_length=32, choices=states)),
            ('start', models.DateTimeField()),
            ('end', models.DateTimeField()),
        ))
        db.send_create_signal('wheeljack', ['Project','BuildLog'])

    def backwards(self):
        db.delete_table('wheeljack_buildlog')
        db.delete_table('wheeljack_project')
