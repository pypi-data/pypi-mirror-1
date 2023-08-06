class WheeljackError(Exception):
    """Base class for all Wheeljack related errors."""

class BuildError(Exception):

    def __init__(self, cmd, revision, start, output):
        self.cmd = cmd
        self.revision = revision
        self.start = start
        self.output = output

    def __str__(self):
        return 'Command: %s failed. Output from executiion:\n\n%s' % (
            self.cmd, self.output)


class RepositoryError(WheeljackError):
    """Error indicating problems with the repository communication."""

    def __init__(self, msg):
        self.msg = msg
