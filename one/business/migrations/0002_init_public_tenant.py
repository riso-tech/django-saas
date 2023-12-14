from django.db import migrations


def update_public_forward(apps, schema_editor):
    """Set site domain and name."""
    Business = apps.get_model("business", "Business")  # noqa
    Domain = apps.get_model("business", "Domain")  # noqa

    # create your public tenant
    tenant = Business(
        schema_name='public',
        code='PUBLIC_SHARED_APP',
        is_active=True,
        name='Public Shared App',
    )
    tenant.save()

    domain = Domain(
        domain='localhost',
        tenant=tenant,
        is_primary=True
    )
    domain.save()


def update_public_backward(apps, schema_editor):
    """Revert site domain and name to default."""
    pass


class Migration(migrations.Migration):
    dependencies = [("business", "0001_initial")]

    operations = [migrations.RunPython(update_public_forward, update_public_backward)]
