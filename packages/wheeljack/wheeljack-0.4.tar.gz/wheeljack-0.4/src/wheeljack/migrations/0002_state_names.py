from wheeljack.models import BuildLog

class Migration:

    state_mapping = dict(
        OK='SUCCESS',
        FAILED='FAILURE')

    def forwards(self):
        self.apply_changes(self.state_mapping)

    def backwards(self):
        reversed_mapping = dict([(value, key) for key, value in
                                 self.state_mapping.iteritems()])
        self.apply_changes(reversed_mapping)

    def apply_changes(self, mapping):
        for log in BuildLog.objects.all():
            log.state = mapping.get(log.state, log.state)
            log.save()
