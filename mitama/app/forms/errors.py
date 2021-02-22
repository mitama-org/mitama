from jinja2 import Template

class ValidationError(Exception):
    template = Template("{{ label }}が適切ではありません")
    def __init__(self, label="", data=""):
        self.label = label
        self.data = data

    @classmethod
    def setTemplate(cls, template = "{{ label }}が適切ではありません"):
        cls.template = Template(template)

    @property
    def message(self):
        return self.template.render(
            label = self.label,
            data = self.data
        )

    def __str__(self):
        return self.message

class EmptyError(ValidationError):
    template = Template("{{ label }}が入力されていません")
    def __init__(self, label=""):
        super().__init__(label, None)

class FormatError(ValidationError):
    template = Template("{{ label }}の形式が間違っています")
    def __init__(self, label="", data=""):
        super().__init__(label, data)

def empty_error(template_string):
    class EmtpyError_(EmptyError):
        template = Template(template_string)
    return EmtpyError_

def format_error(template_string):
    class FormatError_(FormatError):
        template = Template(template_string)
    return FormatError_
