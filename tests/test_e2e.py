import pytest
import pywikibot
from scripts import create_ability_pages, create_ai_profiles


@pytest.fixture(scope="session")
def site():
    return pywikibot.Site()


@pytest.mark.parametrize(
    "fn,title_template",
    [
        (create_ability_pages.generate_pages, "{0}"),
        (create_ai_profiles.generate_ai_profiles, "AIP:{0}"),
    ],
)
def test_compare_wiki(site, fn, title_template):
    errors = []
    for name, text in fn().items():
        title = title_template.format(name)
        page = pywikibot.Page(site, title)
        if not page.text == text:
            errors.append(title)
    assert not errors, f"These pages have text different from the wiki: {errors}"
