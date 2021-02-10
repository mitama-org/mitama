from errors import *

class Field:
    def __init__(
        self,
        label="",
        initial=None,
        regex=None,
        validator=None,
        required=False,
        name=None,
        form_type="text",
        placeholder=None
    ):
        self.required = False
        self.label = label
        self.initial = initial
        self.regex = regex
        self.validator = validator
        self.data = initial
        self.form_type = form_type
        self.placeholder = placeholder

    def reset(self):
        self.data = self.initial

    def validate(self):
        self.value = value
        if self.required and self.value is None:
            raise EmptyError(self.label)
        if self.regex and re.fullmatch(self.regex, self.value) is None:
            raise FormatError(self.label, self.value)
        self.validator(self.value)
        return True
