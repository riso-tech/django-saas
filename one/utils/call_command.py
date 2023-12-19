import io
import sys

from django.core.management import call_command as base_call_command


def call_command(message, data={}):  # noqa
    try:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        base_call_command(message, **data)
        sys.stdout = sys.__stdout__
        return output_buffer.getvalue().splitlines(), True
    except EOFError as e:
        return [str(e)], False
