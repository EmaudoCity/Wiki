from django.test import TestCase
from django.urls import reverse

from . import util


class WikiTests(TestCase):
    def test_index_lists_entries(self):
        response = self.client.get(reverse("encyclopedia:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")
        self.assertContains(response, 'href="/wiki/Python"')

    def test_entry_page_renders_markdown(self):
        response = self.client.get(reverse("encyclopedia:entry", args=["Python"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Python</h1>", html=True)
        self.assertContains(response, "<strong>Python</strong>", html=True)
        self.assertContains(response, "Edit Page")

    def test_missing_entry_returns_404(self):
        response = self.client.get(reverse("encyclopedia:entry", args=["Nope"]))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "was not found", status_code=404)

    def test_search_exact_redirects(self):
        response = self.client.get(reverse("encyclopedia:search"), {"q": "python"})
        self.assertRedirects(response, reverse("encyclopedia:entry", args=["Python"]))

    def test_search_substring_results(self):
        response = self.client.get(reverse("encyclopedia:search"), {"q": "ytho"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")
        self.assertNotContains(response, "Django")

    def test_new_page_creates_entry(self):
        response = self.client.post(reverse("encyclopedia:new"), {
            "title": "TestEntry",
            "content": "# Test\n\nSome **bold** text.",
        })
        self.assertRedirects(response, reverse("encyclopedia:entry", args=["TestEntry"]))
        self.assertIsNotNone(util.get_entry("TestEntry"))

        page = self.client.get(reverse("encyclopedia:entry", args=["TestEntry"]))
        self.assertContains(page, "<h1>Test</h1>", html=True)

        util.save_entry("TestEntry", "")
        import os
        from django.conf import settings
        os.remove(os.path.join(settings.MEDIA_ROOT, "entries", "TestEntry.md"))

    def test_duplicate_new_page_shows_error(self):
        response = self.client.post(reverse("encyclopedia:new"), {
            "title": "Python",
            "content": "duplicate",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_edit_prepopulates_and_saves(self):
        page = self.client.get(reverse("encyclopedia:edit", args=["CSS"]))
        self.assertContains(page, "Cascading Style Sheets")

        response = self.client.post(reverse("encyclopedia:edit", args=["CSS"]), {
            "content": "# CSS\n\nEdited content.",
        })
        self.assertRedirects(response, reverse("encyclopedia:entry", args=["CSS"]))
        self.assertIn("Edited content.", util.get_entry("CSS"))

        # Restore the original entry.
        util.save_entry("CSS", page.context["content"])

    def test_random_redirects_to_an_entry(self):
        response = self.client.get(reverse("encyclopedia:random"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/wiki/", response.url)
