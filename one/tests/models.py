from django.contrib.auth import get_user_model
from django.db.models import CASCADE, SET_NULL, CharField, DateField, DateTimeField, ForeignKey, Model, TextField

User = get_user_model()


class Category(Model):
    name = CharField("Title", max_length=50, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return (
            "id__iexact",
            "name__icontains",
        )

    def related_label(self):
        return f"{self.name} ({self.id})"


class Entry(Model):
    title = CharField("Title", max_length=200)
    category = ForeignKey(Category, on_delete=SET_NULL, related_name="entries", blank=True, null=True)
    category_alt = ForeignKey(
        Category, on_delete=SET_NULL, related_name="entriesalt", to_field="name", blank=True, null=True
    )
    date = DateTimeField("Date")
    body = TextField("Body", blank=True)
    user = ForeignKey(User, on_delete=CASCADE, related_name="entries")
    createdate = DateField("Date (Create)", auto_now_add=True)
    updatedate = DateField("Date (Update)", auto_now=True)

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        ordering = ["-date", "title"]

    def __str__(self):
        return self.title

    @staticmethod
    def autocomplete_search_fields():
        return (
            "id__iexact",
            "title__icontains",
        )
