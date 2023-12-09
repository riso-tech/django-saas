from django.conf import settings

# Base config
CMS_ENABLED = getattr(settings, "CMS_ENABLED", False)

# Link to your Main Admin Site (no slashes at start and end)
# not needed anymore
ADMIN_URL = getattr(settings, "ADMIN_URL", "/admin/")
