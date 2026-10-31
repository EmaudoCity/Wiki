import random
import re

import markdown2
from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse

from . import util


class EntryForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(label="Content", widget=forms.Textarea)


def _find(title):
    """Case-insensitive lookup of an entry's real name."""
    for name in util.list_entries():
        if name.lower() == title.lower():
            return name
    return None


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    name = _find(title)
    content = util.get_entry(name) if name else None
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "message": "The requested page was not found.",
        }, status=404)
    return render(request, "encyclopedia/entry.html", {
        "title": name,
        "content": markdown2.markdown(content),
    })


def search(request):
    query = request.GET.get("q", "").strip()
    name = _find(query) if query else None
    if name:
        return redirect(reverse("encyclopedia:entry", args=[name]))
    results = [e for e in util.list_entries() if query.lower() in e.lower()] if query else []
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "entries": results,
    })


def new(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip()
            if not title or re.search(r"[/\\]", title) or title in (".", ".."):
                form.add_error("title", "Invalid title.")
            elif _find(title):
                form.add_error("title", "An entry with this title already exists.")
            else:
                util.save_entry(title, form.cleaned_data["content"])
                return redirect(reverse("encyclopedia:entry", args=[title]))
        return render(request, "encyclopedia/new.html", {"form": form})
    return render(request, "encyclopedia/new.html", {"form": EntryForm()})


def edit(request, title):
    name = _find(title)
    if name is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "message": "The requested page was not found.",
        }, status=404)
    if request.method == "POST":
        content = request.POST.get("content", "")
        util.save_entry(name, content)
        return redirect(reverse("encyclopedia:entry", args=[name]))
    return render(request, "encyclopedia/edit.html", {
        "title": name,
        "content": util.get_entry(name),
    })


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return redirect(reverse("encyclopedia:index"))
    return redirect(reverse("encyclopedia:entry", args=[random.choice(entries)]))
