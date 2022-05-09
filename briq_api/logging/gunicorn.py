from gunicorn import glogging

class GunicornLoggerOverride(glogging.Logger):
    """Make the Gunicorn Logger propagate messages to the root handler."""

    def __init__(self, cfg):
        super().__init__(cfg)
        self.access_log.propagate = True
        self.error_log.propagate = True
        for handler in self.access_log.handlers:
            self.access_log.handlers.remove(handler)
        for handler in self.error_log.handlers:
            self.error_log.handlers.remove(handler)
