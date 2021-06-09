from flask_wtf import FlaskForm
from werkzeug.datastructures import FileStorage
from wtforms import MultipleFileField as _MultipleFileField
from wtforms.validators import DataRequired, StopValidation
from flask_wtf._compat import abc
from flask_uploads import DATA


class MultipleFileField(_MultipleFileField):
    def process_formdata(self, valuelist):
        valuelist = (x for x in valuelist if isinstance(x, FileStorage) and x)
        data = list(valuelist) or None

        if data is not None:
            self.data = data
        else:
            self.raw_data = ()


class FilesRequired(DataRequired):
    def __call__(self, form, field):
        if not (field.data and all(isinstance(x, FileStorage) and x for x
                                   in field.data)):
            raise StopValidation(
                self.message or field.gettext('This field is required.'),
            )


class FilesAllowed(object):
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        if not (field.data and all(isinstance(x, FileStorage) and x for x
                                   in field.data)):
            return
        for data in field.data:
            filename = data.filename.lower()

            if isinstance(self.upload_set, abc.Iterable):
                if any(filename.endswith('.' + x) for x in self.upload_set):
                    continue

                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension: {extensions}'
                ).format(extensions=', '.join(self.upload_set)))

            if not self.upload_set.file_allowed(data, filename):
                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension.'
                ))


class UploadForm(FlaskForm):
    file = MultipleFileField(validators=[FilesRequired(), FilesAllowed(DATA, 'Data only!')])
