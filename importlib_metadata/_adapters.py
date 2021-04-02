import string
import textwrap
import itertools
import email.message


class Message(email.message.Message):
    def __new__(cls, orig: email.message.Message):
        res = super().__new__(cls)
        vars(res).update(vars(orig))
        return res

    def __init__(self, *args, **kwargs):
        pass

    @property
    def json(self):
        """
        Convert PackageMetadata to a JSON-compatible format
        per PEP 0566.
        """
        # TODO: Need to match case-insensitive
        multiple_use = {
            'Classifier',
            'Obsoletes-Dist',
            'Platform',
            'Project-URL',
            'Provides-Dist',
            'Provides-Extra',
            'Requires-Dist',
            'Requires-External',
            'Supported-Platform',
        }

        def redent(value):
            "Correct for RFC822 indentation"
            if not value or '\n' not in value:
                return value
            return textwrap.dedent(' ' * 8 + value)

        def transform(key):
            value = self.get_all(key) if key in multiple_use else redent(self[key])
            if key == 'Keywords':
                value = value.split(string.whitespace)
            if not value and key == 'Description':
                value = self.get_payload()
            tk = key.lower().replace('-', '_')
            return tk, value

        desc = ['Description'] if self.get_payload() else []
        keys = itertools.chain(self, desc)
        return dict(map(transform, keys))
