import random
import secrets
import markdown2 as m

from django.contrib.admin import forms
from markdown2 import Markdown
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label= "Entry title", widget=forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField( widget=forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8', 'rows': 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def convert_md_to_html(title):
    content = util.get_entry(title)
    markdowner = Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)


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
    entries = util.list_entries()
    css_file = util.get_entry("CSS")
    coffee = util.get_entry("Coffee")
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    markdowner = Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entrytitle": entry,
            "message": f'The page "{entry}" was not found.'
        }, status=404)
    else:
        return render(request, "encyclopedia/entry.html", {
          "entry": markdowner.convert(entryPage),
          "entrytitle": entry,
    })


def search(request):
    value = request.GET.get("q", "")
    if(util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={"entry": value}))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subStringEntries.append(entry)
       
        return render(request, "encyclopedia/index.html", {
            "entries": subStringEntries,
            "search": True,
            "value": value

        })
     
    


def newEntry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is not None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={"entry": title}))
            else:
                return render(request, "encyclopedia/newEntry.html", {
                    "form": form,
                    "existing": True,
                    "entry": title,
                })
        else:
            return render(request, "encyclopedia/newEntry.html", {
                "form": form,
                "existing": False
            })
    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm(),
        "existing": False
    })
          
  
def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entrytitle": entry,
        })
    else:
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/new.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entrytitle": form.fields["title"].initial
        })

       
def random_page(request):
    entries: list[str] = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={"entry": randomEntry}))
ntries)]))
