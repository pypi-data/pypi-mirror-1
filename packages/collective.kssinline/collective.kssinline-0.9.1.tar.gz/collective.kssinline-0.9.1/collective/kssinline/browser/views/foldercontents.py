from zope.interface import implements
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser import foldercontents
from tableview import Table

class FolderContentsView(foldercontents.FolderContentsView):  
    """
    """
    implements(IFolderContentsView)

    def contents_table(self):
        table = FolderContentsTable(self.context, self.request)
        return table.render()

class FolderContentsTable(foldercontents.FolderContentsTable):

    def __init__(self, context, request, contentFilter={}):
        foldercontents.FolderContentsTable.__init__(self, context, request, contentFilter)
        # Redeclare table to use our own table
        url = self.context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons, context=context)

class FolderContentsKSSView(foldercontents.FolderContentsKSSView):
    # todo: check the operation of this class
    table = FolderContentsTable

