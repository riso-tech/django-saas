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

```
