# Business of Django Tenant


### Settings

```python
SHARED_APPS = [
    # Shared apps
    "django_tenants",
    "one.business",
]

TENANT_APPS = [

]

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        # ..
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

MIDDLEWARE = (
    'django_tenants.middleware.main.TenantMainMiddleware',
    #...
)

TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                #...
                "one.business.context_processors.tenant_constants",
            ]
        }
    }
]
```


```html
404.html

{% if exception == BUSINESS_TENANT_REQUIRED_ERROR %}
// Redirect to create business
{% endif %}

```
