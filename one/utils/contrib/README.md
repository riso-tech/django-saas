# Extend Django Admin Functions

If you've ever tried making admin object tools you may have thought, "why can't
this be as easy as making Django Admin Actions?" Well now they can be.

## Quick-Start Guide

In your admin.py:

```python
from one.utils.contrib.admin import DjangoObjectActions, action


class ArticleAdmin(DjangoObjectActions, admin.ModelAdmin):
    @action(label="Publish", description="Submit this article")  # optional
    def publish_this(self, request, obj):
        publish_obj(obj)

    change_actions = ('publish_this',)
    changelist_actions = ('...',)
```

## Usage

Defining new &_tool actions_ is just like defining regular [admin actions]. The
major difference is the functions for `django-object-actions` will take an
object instance instead of a queryset (see _Re-using Admin Actions_ below).

_Tool actions_ are exposed by putting them in a `change_actions` attribute in
your `admin.ModelAdmin`. You can also add _tool actions_ to the main changelist
views too. There, you'll get a queryset like a regular [admin action][admin actions]:

```python
from one.utils.contrib.admin import DjangoObjectActions


class MyModelAdmin(DjangoObjectActions, admin.ModelAdmin):
    @action(
        label="This will be the label of the button",  # optional
        description="This will be the tooltip of the button"  # optional
    )
    def toolfunc(self, request, obj):
        pass

    def make_published(modeladmin, request, queryset):
        queryset.update(status='p')

    change_actions = ('toolfunc',)
    changelist_actions = ('make_published',)
```

Just like admin actions, you can send a message with `self.message_user`.
Normally, you would do something to the object and return to the same url, but
if you return a `HttpResponse`, it will follow it (hey, just like [admin
actions]!).

If your admin modifies `get_urls`, `change_view`, or `changelist_view`,
you'll need to take extra care because `django-object-actions` uses them too.

### Re-using Admin Actions

If you would like a preexisting admin action to also be an _object action_, add
the `takes_instance_or_queryset` decorator to convert object instances into a
queryset and pass querysets:

```python
from one.utils.contrib.admin import DjangoObjectActions, takes_instance_or_queryset


class RobotAdmin(DjangoObjectActions, admin.ModelAdmin):
    # ... snip ...

    @takes_instance_or_queryset
    def tighten_lug_nuts(self, request, queryset):
        queryset.update(lugnuts=F('lugnuts') - 1)

    change_actions = ['tighten_lug_nuts']
    actions = ['tighten_lug_nuts']
```

[admin actions]: https://docs.djangoproject.com/en/stable/ref/contrib/admin/actions/

### Customizing _Object Actions_

To give the action some a helpful title tooltip, you can use the `action` decorator
and set the description argument.

```python
@action(description="Increment the vote count by one")
def increment_vote(self, request, obj):
    obj.votes = obj.votes + 1
    obj.save()
```

Alternatively, you can also add a `short_description` attribute,
similar to how admin actions work:

```python
def increment_vote(self, request, obj):
    obj.votes = obj.votes + 1
    obj.save()


increment_vote.short_description = "Increment the vote count by one"
```

By default, Django Object Actions will guess what to label the button
based on the name of the function. You can override this with a `label`
attribute:

```python
@action(label="Vote++")
def increment_vote(self, request, obj):
    obj.votes = obj.votes + 1
    obj.save()
```

or

```python
def increment_vote(self, request, obj):
    obj.votes = obj.votes + 1
    obj.save()


increment_vote.label = "Vote++"
```

If you need even more control, you can add arbitrary attributes to the buttons
by adding a Django widget style
[attrs](https://docs.djangoproject.com/en/stable/ref/forms/widgets/#django.forms.Widget.attrs)
attribute:

```python
@action(attrs={'class': 'addlink'})
def increment_vote(self, request, obj):
    obj.votes = obj.votes + 1
    obj.save()
```

or

```python
def increment_vote(self, request, obj):
    obj.votes = obj.votes + 1
    obj.save()


increment_vote.attrs = {
    'class': 'addlink',
}
```

### Programmatically Disabling Actions

You can programmatically disable registered actions by defining your own
custom `get_change_actions()` method. In this example, certain actions
only apply to certain object states (e.g. You should not be able to
close an company account if the account is already closed):

```python
def get_change_actions(self, request, object_id, form_url):
    actions = super(PollAdmin, self).get_change_actions(request, object_id, form_url)
    actions = list(actions)
    if not request.user.is_superuser:
        return []

    obj = self.model.objects.get(pk=object_id)
    if obj.question.endswith('?'):
        actions.remove('question_mark')

    return actions
```

The same is true for changelist actions with `get_changelist_actions`.


## More Examples

Making an action that links off-site:

```python
def external_link(self, request, obj):
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect(f'https://example.com/{obj.id}')
```

## Limitations

1. Expects functions to be methods of the model admin. While Django gives you a lot more options for their admin
   actions.
2. Security. This has been written with the assumption that everyone in the Django admin belongs there. Permissions
   should be enforced in your own actions irregardless of what this provides. Better default security is planned for the
   future.
