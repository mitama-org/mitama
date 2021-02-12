from jinja2 import Template

class ValidationError(Exception):
    template = Template("Something wrong with {{ label }}")
    def __init__(self, label="", data=""):
        self.label = label
        self.data = data

    @classmethod
    def setTemplate(cls, template = "Something is wrong with {{ label }}"):
        cls.template = Template(template)

    @property
    def message(self):
        return self.template.render(
            label = self.label,
            data = self.data
        )

class EmptyError(ValidationError):
    template = Template("{{ label }} is required, but it is emtpy.")
    def __init__(self, label=""):
        super().__init__(label, None)

class FormatError(ValidationError):
    template = Template("Invalid format for {{ label }}.")
    def __init__(self, label="", value=""):
        super().__init__(label, value)
