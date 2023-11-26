from django.db import migrations


def update_business_forward(apps, schema_editor):
    """Set site domain and name."""
    Client = apps.get_model("business", "Client")
    Domain = apps.get_model("business", "Domain")

    # create your public tenant
    tenant = Client(
        schema_name='public',
        name='Public Shared App',
        paid_until='2099-12-31',
        on_trial=False
    )
    tenant.save()

    domain = Domain()
    domain.domain = 'public.localhost'
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()


def update_business_backward(apps, schema_editor):
    """Revert site domain and name to default."""
    pass


class Migration(migrations.Migration):
    dependencies = [("business", "0001_initial")]

    operations = [migrations.RunPython(update_business_forward, update_business_backward)]
