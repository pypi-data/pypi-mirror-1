BLOG
====

Abstract
--------

This is a test for the mailtoplone.base BlogMailDropBox


Setup test environment::

    >>> self.setRoles(('Manager',))

Create a folder and mark with the IBlogMailDropBoxMarker::

    >>> from zope.interface import alsoProvides
    >>> from mailtoplone.base.interfaces import IBlogMailDropBoxMarker
    >>> self.portal.invokeFactory('Folder', 'blog')
    'blog'
    >>> alsoProvides(self.portal.blog, IBlogMailDropBoxMarker)
    >>> IBlogMailDropBoxMarker.providedBy(self.portal.blog)
    True

Now that the folder is marked we can use our adapter on it::

    >>> from mailtoplone.base.interfaces import IMailDropBox
    >>> IMailDropBox(self.portal.blog).drop('test')
    
Inside the blog folder, should now be a object of type news::

    >>> len(self.portal.blog.objectIds()) == 1
    True
    >>> self.portal.blog.listFolderContents()[0].meta_type
    'ATNewsItem'
    >>> self.portal.blog.listFolderContents()[0].getText()
    '<p>test</p>'

::

    vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:

