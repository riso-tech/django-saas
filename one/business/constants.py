BUSINESS_TENANT_REQUIRED_ERROR = "BusinessTenantRequired"
ERROR_BUSINESS_NOT_FOUND_TEMPLATE_NAME = "business_required.html"

ERROR_PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <title>%(title)s</title>
</head>
<body>
  <h1>%(title)s</h1><p>%(details)s</p>
</body>
</html>
"""
