"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/links.py $
$Id: links.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from datetime import datetime
from dulcinea.attachable import Attachable
from dulcinea.category import Category, Categorized, CategoryDatabase
from dulcinea.item import Item, ItemFolder
from dulcinea.spec import boolean, sequence, spec, init, add_getters_and_setters
from dulcinea.spec import specify, string
from dulcinea.util import wrap_paragraphs, sanitize_url
from durus.persistent import Persistent
import random

class LinkItem(Item, Attachable, Categorized):

    link_url_is = spec(
        (string, None),
        "Link to relevant target URL")
    text_is = spec(
        (string, None),
        "A few sentences describing the link.")
    email_is = spec(
        (string, None),
        "Submitter's e-mail address")
    first_class_is = spec(
        boolean,
        "Flag to indicate that this link can be shown in a prominent "
        "place like the home page of a site")

    def __init__(self):
        Item.__init__(self)
        Attachable.__init__(self)
        Categorized.__init__(self)
        init(self, first_class=False)

    def get_allowed_mime_types(self, user=None):
         """() -> [string]
         """
         if user and user.is_admin():
             return Attachable.get_allowed_mime_types(self)
         else:
             return ["image/gif", "image/jpeg", "image/png",
                     "image/tiff", "image/x-ms-bmp"]


    def set_link_url(self, url):
        specify(self,
                link_url=sanitize_url(url),
                timestamp=datetime.now())

    def is_first_class(self):
        return self.first_class

    def get_local_url(self):
        "Return the URL to this Item"
        return "/links/%s/" % self.get_key()

    def as_text(self):
        return "%s\n\n%s\nURL: %s" % (self.get_title(), self.get_text(),
                                      self.get_link_url())
    def as_email(self):
        body = "%s\n" % self.get_title()
        if self.get_link_url():
            body += "(%s)\n" % self.get_link_url()
        body += "\n%s" % wrap_paragraphs(self.get_text())
        return self.title, body

add_getters_and_setters(LinkItem)


class LinkFolder(ItemFolder, CategoryDatabase):
    """
    To add a new leaf Category, create the Category instance, set it's 'name'
    and 'label', choose a parent Category from the LinkFolder.categories
    dictionary and call it's 'add_child' to add the new category, finally call
    LinkFolder.add_category to add the new Category to categories
    """

    def __init__(self):
        ItemFolder.__init__(self)
        CategoryDatabase.__init__(self)
        links_category = Category(name='all')
        links_category.set_label('All Links')
        self.add_category(links_category)

    def links_with_category(self, category):
        return [link for link in self.get_items() if link.in_category(category)]

    def get_all_links(self):
        return self.get_items()

    def get_first_class_links(self):
        return [link for link in self.get_items() if link.is_first_class()]

    def random_first_class_link(self):
        first_class_links = self.get_first_class_links()
        if first_class_links:
            return random.choice(first_class_links)
        return None

def sort_reverse_by_date(link1, link2):
    # Sort links cronologically with most recent first
    return cmp(link2.get_timestamp(), link1.get_timestamp())

def sort_by_title(link1, link2):
    title1 = (link1.get_title() and link1.get_title().lower()) or None
    title2 = (link2.get_title() and link2.get_title().lower()) or None
    return cmp(title1, title2)


class LinkTripleDatabase(Persistent):

    links_is = sequence(element_spec=(string, string, (string, None)),
                        container_spec=list)

    def __init__(self):
        self.links = []

    def __getitem__(self, index):
        return self.links[index]

    def __setitem__(self, index, link):
        self._p_note_change()
        self.links[index] = link

    def __delitem__(self, index):
        self._p_note_change()
        del self.links[index]

    def insert_link(self, link, index=None):
        self._p_note_change()
        if index is None:
            index = len(self.links)
        assert 0 <= index <= len(self.links), index
        links_after = self.links[index:]
        self.links = self.links[:index]
        self.links.append(link)
        self.links.extend(links_after)


add_getters_and_setters(LinkTripleDatabase)

