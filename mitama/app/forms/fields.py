from . import errors
import re

class Field:
    ValidationError = errors.ValidationError
    EmptyError = errors.EmptyError
    FormatError = errors.FormatError
    def __init__(
        self,
        label="",
        initial=None,
        regex=None,
        validator=None,
        required=False,
        name=None,
        form_type="text",
        placeholder=None,
        listed=False
    ):
        self.required = required
        self.label = label
        self.initial = initial
        self.regex = regex
        self.validator = validator
        self.form_type = form_type
        self.placeholder = placeholder
        self.name = name
        self.listed = listed

    def instance(self):
        return FieldInstance(
            label=self.label,
            initial=self.initial,
            regex=self.regex,
            validator=self.validator,
            required=self.required,
            name=self.name,
            form_type=self.form_type,
            placeholder=self.placeholder,
            listed=self.listed,
            validation_error=self.ValidationError,
            empty_error=self.EmptyError,
            format_error=self.FormatError,
        )

class DictField(Field):
    def __init__(
        self,
        **kwargs
    ):
        super().__init__(
            **kwargs
        )

    def instance(self):
        return DictFieldInstance(
            label=self.label,
            initial=self.initial,
            regex=self.regex,
            validator=self.validator,
            required=self.required,
            name=self.name,
            form_type=self.form_type,
            placeholder=self.placeholder,
            listed=self.listed,
            validation_error=self.ValidationError,
            empty_error=self.EmptyError,
            format_error=self.FormatError,
        )

class FileField(Field):
    def __init__(
        self,
        accept=None,
        max_file_size=None,
        **kwargs
    ):
        kwargs["form_type"] = "file"
        super().__init__(
            **kwargs
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
            max_file_size=self.max_file_size,
            validation_error=self.ValidationError,
            empty_error=self.EmptyError,
            format_error=self.FormatError,
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
        placeholder=None,
        listed=False,
        validation_error=errors.ValidationError,
        empty_error=errors.EmptyError,
        format_error=errors.FormatError,
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
        self.listed=listed
        self.validation_error = validation_error
        self.empty_error = empty_error
        self.format_error = format_error

    def reset(self):
        self.data = self.initial

    def validate(self):
        if self.required and self.data is None:
            raise self.empty_error(self.label)
        if self.data is not None and self.regex and re.fullmatch(self.regex, self.data) is None:
            raise self.format_error(self.label, self.data)
        if self.data is not None and self.validator: self.validator(self.data)
        return True

class DictFieldInstance:
    def __init__(
        self,
        label="",
        initial=None,
        regex=None,
        validator=None,
        required=False,
        name=None,
        form_type="text",
        placeholder=None,
        listed=False,
        validation_error=errors.ValidationError,
        empty_error=errors.EmptyError,
        format_error=errors.FormatError,
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
        self.listed=listed
        self.validation_error = validation_error
        self.empty_error = empty_error
        self.format_error = format_error

    def reset(self):
        self.data = self.initial

    def validate(self):
        if self.required and self.data is None:
            raise self.empty_error(self.label)
        if self.data is not None and self.regex and re.fullmatch(self.regex, self.data) is None:
            raise self.format_error(self.label, self.data)
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
        max_file_size=None,
        validation_error=errors.ValidationError,
        empty_error=errors.EmptyError,
        format_error=errors.FormatError,
    ):
        super().__init__(
            required=required,
            label=label,
            initial=initial,
            validator=validator,
            name=name,
            placeholder=placeholder,
            form_type="file",
            validation_error=validation_error,
            empty_error=empty_error,
            format_error=format_error,
        )
        self.accept = accept
        self.max_file_size = max_file_size
        self._data = None
        self._bin = None

    def validate(self):
        if self.required and self.data is None:
            raise self.empty_error(self.label)
        if self.data is not None and self.regex and re.fullmatch(self.regex, self.data) is None:
            raise self.format_error(self.label, self.data)
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

