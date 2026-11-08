import random

import markdown2
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util


def _entry_exists(title):
    """Case-insensitive existence check so titles stay unique."""
    return any(entry.lower() == title.lower() for entry in util.list_entries())


def _find_entry_title(title):
    """Return the stored title matching case-insensitively, or None."""
    for entry in util.list_entries():
        if entry.lower() == title.lower():
            return entry
    return None


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "message": f'The page "{title}" was not found.'
        }, status=404)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(content, extras=["fenced-code-blocks", "tables"])
    })


def search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return render(request, "encyclopedia/search.html", {
            "query": query,
            "entries": []
        })

    # An exact (case-insensitive) match goes straight to that entry.
    exact = _find_entry_title(query)
    if exact is not None:
        return HttpResponseRedirect(reverse("entry", args=[exact]))

    # Otherwise show every entry containing the query as a substring.
    results = [entry for entry in util.list_entries()
               if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "entries": results
    })


def new(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "")

        if not title:
            return render(request, "encyclopedia/new.html", {
                "error": "Please provide a title for the new page.",
                "title_value": title,
                "content_value": content
            })

        if _entry_exists(title):
            return render(request, "encyclopedia/new.html", {
                "error": f'An encyclopedia entry named "{title}" already exists.',
                "title_value": title,
                "content_value": content
            })

        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=[title]))

    return render(request, "encyclopedia/new.html")


def edit(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "message": f'The page "{title}" was not found.'
        }, status=404)

    if request.method == "POST":
        new_content = request.POST.get("content", "")
        util.save_entry(title, new_content)
        return HttpResponseRedirect(reverse("entry", args=[title]))

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "title": "Random Page",
            "message": "There are no encyclopedia entries yet."
        }, status=404)

    return HttpResponseRedirect(reverse("entry", args=[random.choice(entries)]))
