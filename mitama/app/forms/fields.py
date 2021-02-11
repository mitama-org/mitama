from .errors import *
import re

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
        self.required = required
        self.label = label
        self.initial = initial
        self.regex = regex
        self.validator = validator
        self.form_type = form_type
        self.placeholder = placeholder
        self.name = name

    def instance(self):
        return FieldInstance(
            label=self.label,
            initial=self.initial,
            regex=self.regex,
            validator=self.validator,
            required=self.required,
            name=self.name,
            form_type=self.form_type,
            placeholder=self.placeholder
        )

class FieldInstance:
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
        self.required = required
        self.label = label
        self.initial = initial
        self.regex = regex
        self.validator = validator
        self.data = initial
        self.form_type = form_type
        self.placeholder = placeholder
        self.name = name

    def reset(self):
        self.data = self.initial

    def validate(self):
        if self.required and self.data is None:
            raise EmptyError(self.label)
        if self.data is not None and self.regex and re.fullmatch(self.regex, self.data) is None:
            raise FormatError(self.label, self.data)
        if self.data is not None and self.validator: self.validator(self.data)
        return True
