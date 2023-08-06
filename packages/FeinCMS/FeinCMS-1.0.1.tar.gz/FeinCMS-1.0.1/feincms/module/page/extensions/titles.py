"""
Sometimes, a single title is not enough, you'd like subtitles, and maybe differing
titles in the navigation and in the <title>-tag.
This extension lets you do that.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _


def register(cls, admin_cls):
    cls.add_to_class('_content_title', models.TextField(_('content title'), blank=True,
        help_text=_('The first line is the main title, the following lines are subtitles.')))
    cls.add_to_class('_page_title', models.CharField(_('page title'), max_length=100, blank=True,
        help_text=_('Page title for browser window. Same as title by default.')))

    def _page_title(self):
        """
        Use this for the browser window (<title>-tag in the <head> of the HTML document)
        """

        if self._page_title:
            return self._page_title
        return self.content_title

    cls.page_title = property(_page_title)

    def _content_title(self):
        """
        This should be used f.e. for the <h1>-tag
        """

        if not self._content_title:
            return self.title

        return self._content_title.splitlines()[0]

    cls.content_title = property(_content_title)

    def _content_subtitle(self):
        return u'\n'.join(self._content_title.splitlines()[1:])

    cls.content_subtitle = property(_content_subtitle)

