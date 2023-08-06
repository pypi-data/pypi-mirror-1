# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: interfaces.py 6338 2008-07-22 14:46:32Z ctheune $

import zope.interface
import zope.interface.common.mapping
import zope.schema


class IMAPError(Exception):
    """An error raised due to a failed IMAP command."""


class IAccountContent(zope.interface.Interface):
    """Something that resides in the object hierarchy of an account.

    This basically means that it can (in general) be associated with an
    account and that it has a name and a parent that locates it in the
    hierarchy.

    The hierarchy may not be unambiguously traversable because of separate
    name spaces, i.e. for folders and messages.

    Specific applications have to pay attention to the actual object they are
    trying to establish a path for and keep markers that identifies those
    namespaces for later traversal.

    """

    name = zope.interface.Attribute('The name.')

    parent = zope.interface.Attribute('The parent node in the hierarchy.')


class IMessage(IAccountContent):
    """A message.

    """

    headers = zope.interface.Attribute(
        'A dictionary-like object providing access to the headers.')

    raw = zope.interface.Attribute(
        'The raw text content of the whole message. '
        'Includes headers and body. No encoding conversions are applied. ')

    text = zope.interface.Attribute(
        'The body of the message as text/plain.')

    body = zope.interface.Attribute(
        'The message\'s body structure and content given as an IBodyPart object.') 


class IFolders(zope.interface.common.mapping.IMapping):
    """A mapping object for accessing folders located in IFolderContainers.
    """


class IMessages(zope.interface.common.mapping.IMapping):
    """A mapping object for accessing messages located in IMessageContainers.
    """


class IFolderContainer(zope.interface.Interface):
    """An object that contains folders."""

    folders = zope.schema.Object(
        title=u'The sub-folders of this folder',
        schema=IFolders)


class IMessageContainer(zope.interface.Interface):
    """An object that contains messages."""

    messages = zope.schema.Object(
        title=u'The messages of this folder.',
        schema=IMessages)


class IAccount(IFolderContainer):
    """An IMAP account.

    Provides live access to the account on the server.

    """


class IFolder(IFolderContainer, IMessageContainer, IAccountContent):
    """An IMAP folder.

    Contains messages and other folders.

    """


class IBodyPart(zope.interface.Interface):
    """A part of a message body.

    A dictionary-like object with the message body part's parameters as keys.

    If the body part is of the major content type `multipart` then the `parts`
    attribute contains the sub-parts.

    """

    parts = zope.interface.Attribute('A list of sub-parts.')

    def __getitem__(key):
        """Access the property `key` from the body part."""

    def get(key, default=None):
        """Access the property `key` from the body part or return default."""

    def fetch():
        """Return a file object containing the data of the body."""
