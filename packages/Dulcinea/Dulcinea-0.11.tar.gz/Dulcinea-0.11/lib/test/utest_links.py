"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_links.py $
$Id: utest_links.py 27429 2005-09-15 14:13:43Z dbinger $
"""
from dulcinea.contact import Contact
from dulcinea.links import LinkItem, LinkFolder, LinkTripleDatabase
from dulcinea.links import sort_by_title, sort_reverse_by_date
from sancho.utest import UTest


class LinksTest (UTest):

    class AdminContact(Contact):

        def is_admin(self):
            return True

    def check_link_triple_db(self):
        self.ltdb = LinkTripleDatabase()
        assert len(self.ltdb.get_links()) == 0
        self.ltdb.set_links([('a', 'b', 'c'), ('1', '2', '3')])
        assert len(self.ltdb.get_links()) == 2
        assert self.ltdb[0] == ('a', 'b', 'c')
        self.ltdb.insert_link(('A', 'B', 'C'), 1)
        assert len(self.ltdb.get_links()) == 3
        assert self.ltdb.get_links() == [('a', 'b', 'c'),
                                         ('A', 'B', 'C'),
                                         ('1', '2', '3')]
        self.ltdb[2] = ('4', '5', '6')
        assert self.ltdb.get_links() == [('a', 'b', 'c'),
                                         ('A', 'B', 'C'),
                                         ('4', '5', '6')]
        del self.ltdb[0]
        assert self.ltdb.get_links() == [('A', 'B', 'C'),
                                         ('4', '5', '6')]

    def check_link(self):
        self.link = LinkItem()
        self.link.set_link_url('http://www.mems-exchange.org')
        self.link.get_link_url()
        self.link.set_text('hi')
        assert self.link.get_text() == 'hi'
        self.link.set_email('hi')
        assert self.link.get_email() == 'hi'
        self.link.as_text()
        self.link.as_email()
        assert self.link.is_approved() == False
        self.link.set_approved(True)
        assert self.link.is_approved() == True
        self.link.get_allowed_mime_types()
        self.link.get_allowed_mime_types(user=self.AdminContact('superuser'))
        assert self.link.get_local_url() == '/links/None/'
        self.link2 = LinkItem()
        [self.link, self.link2].sort(sort_reverse_by_date)
        [self.link, self.link2].sort(sort_by_title)

    def check_link_folder(self):
        self.link_db = LinkFolder()
        self.link_db.get_category('foo')
        self.link_db.links_with_category('foo')


if __name__ == "__main__":
    LinksTest()
