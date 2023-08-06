class TemplateError(Exception):
    """Raised when a general Error in the templates.py module occurs
    Attributes:
        message -- explanation of what the specific error is.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class PluginError(Exception):
    pass


