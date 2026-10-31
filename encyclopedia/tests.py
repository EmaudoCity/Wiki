from django.test import TestCase
from django.urls import reverse

from . import util


class WikiTests(TestCase):
    def test_entry(self):
        r = self.client.get("/wiki/Python")
        self.assertContains(r, "<strong>programming language</strong>")

    def test_missing(self):
        self.assertEqual(self.client.get("/wiki/Nope").status_code, 404)

    def test_search(self):
        self.assertRedirects(self.client.get("/search?q=python"), "/wiki/Python")
        self.assertContains(self.client.get("/search?q=ytho"), "Python")

    def test_new_duplicate(self):
        r = self.client.post(reverse("encyclopedia:new"), {"title": "Python", "content": "x"})
        self.assertContains(r, "already exists")

    def test_edit(self):
        original = util.get_entry("Git")
        try:
            r = self.client.post("/wiki/Git/edit", {"content": "# Git\n\nnew"})
            self.assertRedirects(r, "/wiki/Git")
            self.assertContains(self.client.get("/wiki/Git"), "new")
        finally:
            util.save_entry("Git", original)

    def test_random(self):
        self.assertEqual(self.client.get("/random").status_code, 302)
