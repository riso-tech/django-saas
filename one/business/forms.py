from django.forms import BooleanField, CharField, Form


class CreateTenantForm(Form):
    schema_name = CharField()
    code = CharField()
    is_active = BooleanField()
    name = CharField()
    description = CharField()
    domain_domain = CharField()
    domain_is_primary = BooleanField()
