Django GUID attaches a unique correlation ID/request ID to all your log
outputs for every request. In other words, all logs connected to a
request now has a unique ID attached to it, making debugging simple.

Django GUID uses `ContextVar` to store and access the GUID.

#### Examples

Log output with a GUID:

```flex
INFO ... [773fa6885e03493498077a273d1b7f2d] project.views This is a DRF view log, and should have a GUID.
WARNING ... [773fa6885e03493498077a273d1b7f2d] project.services.file Some warning in a function
INFO ... [0d1c3919e46e4cd2b2f4ac9a187a8ea1] project.views This is a DRF view log, and should have a GUID.
INFO ... [99d44111e9174c5a9494275aa7f28858] project.views This is a DRF view log, and should have a GUID.
WARNING ... [0d1c3919e46e4cd2b2f4ac9a187a8ea1] project.services.file Some warning in a function
WARNING ... [99d44111e9174c5a9494275aa7f28858] project.services.file Some warning in a function
```

Log output without a GUID:

```flex
INFO ... project.views This is a DRF view log, and should have a GUID.
WARNING ... project.services.file Some warning in a function
INFO ... project.views This is a DRF view log, and should have a GUID.
INFO ... project.views This is a DRF view log, and should have a GUID.
WARNING ... project.services.file Some warning in a function
WARNING ... project.services.file Some warning in a function
```

See the [documentation](https://django-guid.readthedocs.io) for more
examples.

# Settings

Package settings are added in your `settings.py`:

```python
DJANGO_GUID = {
    'GUID_HEADER_NAME': 'Correlation-ID',
    'VALIDATE_GUID': True,
    'RETURN_HEADER': True,
    'EXPOSE_HEADER': True,
    'INTEGRATIONS': [],
    'IGNORE_URLS': [],
    'UUID_LENGTH': 32,
}
```

**Optional Parameters**

- `GUID_HEADER_NAME`

  : The name of the GUID to look for in a header in an incoming
  request. Remember that it\'s case insensitive.

         Default: Correlation-ID

- `VALIDATE_GUID`

  : Whether the `GUID_HEADER_NAME` should be validated or not. If
  the GUID sent to through the header is not a valid GUID
  (`uuid.uuid4`).

         Default: True

- `RETURN_HEADER`

  : Whether to return the GUID (Correlation-ID) as a header in the
  response or not. It will have the same name as the
  `GUID_HEADER_NAME` setting.

         Default: True

- `EXPOSE_HEADER`

  : Whether to return `Access-Control-Expose-Headers` for the GUID
  header if `RETURN_HEADER` is `True`, has no effect if
  `RETURN_HEADER` is `False`. This is allows the JavaScript Fetch
  API to access the header when CORS is enabled.

         Default: True

- `INTEGRATIONS`

  : Whether to enable any custom or available integrations with
  `django_guid`. As an example, using `SentryIntegration()` as an
  integration would set Sentry\'s `transaction_id` to match the
  GUID used by the middleware.

         Default: \[\]

- `IGNORE_URLS`

  : URL endpoints where the middleware will be disabled. You can put
  your health check endpoints here.

         Default: \[\]

- `UUID_LENGTH`

  : Lets you optionally trim the length of the package generated
  UUIDs.

         Default: 32

### Configuration

Once settings have set up, add the following to your projects\'
`settings.py`:

#### Logging Configuration

Add `one.libraries.guid.log_filters.CorrelationId` as a filter in your
`LOGGING` configuration:

```python
LOGGING = {
    ...
    'filters': {
        'correlation_id': {
            '()': 'one.libraries.guid.log_filters.CorrelationId'
        }
    }
}
```

Put that filter in your handler:

```python
LOGGING = {
    ...
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'medium',
            'filters': ['correlation_id'],
        }
    }
}
```

And make sure to add the new `correlation_id` filter to one or all of
your formatters:

```python
LOGGING = {
    ...
    'formatters': {
        'medium': {
            'format': '%(levelname)s %(asctime)s [%(correlation_id)s] %(name)s %(message)s'
        }
    }
}
```

If these settings were confusing, please have a look in the demo
projects\'
[settings.py](https://github.com/snok/django-guid/blob/master/demoproj/settings.py)
file for a complete example.

## 4. Django GUID Logger (Optional)

If you wish to see the Django GUID middleware outputs, you may configure
a logger for the module. Simply add django_guid to your loggers in the
project, like in the example below:

```python
LOGGING = {
    ...
    'loggers': {
        'django_guid': {
            'handlers': ['console', 'logstash'],
            'level': 'WARNING',
            'propagate': False,
        }
    }
}
```

This is especially useful when implementing the package, if you plan to
pass existing GUIDs to the middleware, as misconfigured GUIDs will not
raise exceptions, but will generate warning logs.
