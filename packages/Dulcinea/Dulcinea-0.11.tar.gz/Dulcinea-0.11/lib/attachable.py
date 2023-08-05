"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/attachable.py $
$Id: attachable.py 27535 2005-10-11 15:47:38Z dbinger $

Provides the Attachable mixin class that allows objects to to have
file attachments.
"""
from datetime import datetime
from dulcinea.spec import spec, specify, add_getters_and_setters, require, string
from dulcinea.stored_file import StoredFile, MIME_TYPES
from dulcinea.user import DulcineaUser

class Attachment:
    """
    Stores properties of an attachment relationship between an Attachable
    object and a StoredFile.
    """

    file_is = spec(
        StoredFile,
        "the file attached")
    owner_is = spec(
        DulcineaUser,
        "the owner of this association")
    date_is = spec(
        datetime,
        "date this attachment was created")
    filename_is = spec(
        string,
        "the filename to use when downloading the file")
    description_is = spec(
        (None, string),
        "a description of the file")

    def __init__(self, file, owner):
        specify(self,
             file=file,
             owner=owner,
             date=datetime.now(),
             filename=file.get_filename(),
             description=file.get_description())

    def open(self):
        return self.file.open()

    def get_file_id(self):
        return self.file.get_id()

    def get_size(self):
        return self.file.get_size()

    def get_mime_type(self):
        return self.file.get_mime_type()

    def has_manage_access(self, user):
        return (user and (user is self.owner or user.is_admin()))

    def is_image(self):
        return self.get_mime_type().startswith('image/')

add_getters_and_setters(Attachment)


class Attachable:

    attachments_is = spec(
        [Attachment],
        "attachments connected to this object")

    def __init__(self, attachments=None):
        specify(self, attachments=list(attachments or []))

    def clear_attachments(self):
        specify(self, attachments=[])

    def get_attachments(self):
        """() -> [Attachment]
        Retrieve a list of the attachments for this object.
        """
        return self.attachments

    def get_attached_files(self):
        """() -> [StoredFile]
        Retrieve a list of the file objects attached to this object.
        """
        return [a.get_file() for a in self.attachments]

    def add_attachment(self, attachment):
        require(attachment, Attachment)
        for existing_attachment in self.attachments:
            if existing_attachment.get_file_id() == attachment.get_file_id():
                return
        self.attachments = self.attachments + [attachment]

    def get_attachment(self, id):
        """(id : string) -> Attachment | None
        """
        for attachment in self.attachments:
            if attachment.get_file_id() == id:
                return attachment
        return None

    def attach_file(self, stored_file, user):
        """(stored_file: StoredFile)
        Attach a file to this object.
        """
        files = self.attachments[:]
        files.append(Attachment(stored_file, user))
        self.attachments = files

    def detach_attachment(self, attachment):
        """(attachment: Attachment)
        Detach an attachment from this object.
        """
        require(attachment, Attachment)
        files = self.attachments[:]
        files.remove(attachment)
        self.attachments = files

    def attachment_modified(self, attachment, user):
        """(attachment : Attachment, user : DulcineaUser)

        'attachment' was modified by 'user'.
        Override this method to intercept modification activity for attachments
        """
        pass

    def get_allowed_mime_types(self, user=None):
        """() -> [string]

        Override to restrict the types of files that can be attached
        """
        return [mime_type[0] for mime_type in MIME_TYPES]


