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

class FileField(Field):
    def __init__(
        self,
        label="",
        initial=None,
        validator=None,
        required=False,
        name=None,
        placeholder=None,
        accept=None,
        max_file_size=None
    ):
        super().__init__(
            required=required,
            label=label,
            initial=initial,
            validator=validator,
            name=name,
            placeholder=placeholder,
            form_type="file"
        )
        self.accept = None
        self.max_file_size = None

    def instance(self):
        return FileFieldInstance(
            required=self.required,
            label=self.label,
            initial=self.initial,
            validator=self.validator,
            name=self.name,
            placeholder=self.placeholder,
            accept=self.accept,
            max_file_size=self.max_file_size
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

class FileFieldInstance(FieldInstance):
    def __init__(
        self,
        label="",
        initial=None,
        regex=None,
        validator=None,
        required=False,
        name=None,
        accept=None,
        placeholder=None,
        max_file_size=None
    ):
        super().__init__(
            required=required,
            label=label,
            initial=initial,
            validator=validator,
            name=name,
            placeholder=placeholder,
            form_type="file"
        )
        self.accept = accept
        self.max_file_size = max_file_size
        self._data = None
        self._bin = None

    def validate(self):
        if self.required and self.data is None:
            raise EmptyError(self.label)
        if self.data is not None and self.regex and re.fullmatch(self.regex, self.data) is None:
            raise FormatError(self.label, self.data)
        if self.data is not None and self.validator: self.validator(self.data)
        return True

    @property
    def data(self):
        if self._data is not None:
            if self._bin is not None:
                return self._bin
            else:
                self._bin = self._data.file.read()
                return self._bin
        elif self.initial is not None:
            return self.initial
        else:
            return None

    @data.setter
    def data(self, value):
        self._data = value
