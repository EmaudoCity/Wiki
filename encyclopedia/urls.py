from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("newEntry", views.newEntry, name="newEntry"),
    path("random", views.random_page, name="random"),
    path("wiki/<str:edit>", views.edit, name="edit"),
    path("wiki/<str:entry>", views.entry, name="entry"),
]
