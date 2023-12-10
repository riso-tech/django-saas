import datetime
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CASCADE, SET_NULL, CharField, DateField, DateTimeField, ForeignKey, Model, TextField
from django.utils import timezone

User = get_user_model()


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_recently.admin_order_field = "pub_date"
    was_published_recently.boolean = True
    was_published_recently.short_description = "Published recently?"


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __str__(self):
        return self.choice_text


class Comment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.comment or ""


class RelatedData(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    extra_data = models.TextField(blank=True, default="")

    def __str__(self):
        return self.extra_data or self.id


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
