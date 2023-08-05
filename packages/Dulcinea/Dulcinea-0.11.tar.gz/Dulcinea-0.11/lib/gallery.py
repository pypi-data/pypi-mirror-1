"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/gallery.py $
$Id: gallery.py 27379 2005-09-13 14:16:42Z dbinger $
"""
from dulcinea.attachable import Attachable
from dulcinea.base import DulcineaPersistent


class Gallery (DulcineaPersistent, Attachable):

    def get_allowed_mime_types(self, user=None):
        return ['image/jpeg',
                'image/gif',
                'image/png']

