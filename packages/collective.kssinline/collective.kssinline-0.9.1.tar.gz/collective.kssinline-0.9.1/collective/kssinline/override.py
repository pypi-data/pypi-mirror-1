from archetypes.kss.fields import ATFieldDecoratorView
from archetypes.kss.commands.validation import ValidationCommands
from Acquisition import aq_inner

class KssInlineATFieldDecoratorView(ATFieldDecoratorView):

    def getKssClasses(self, fieldname, templateId=None, macro=None, target=None):
        result = ATFieldDecoratorView.getKssClasses(self, fieldname, templateId, macro, target)
        if result:
            # hedley: UID must be present to enable override of context.
            # This should happen in future versions of archetypes.kss / Archetypes.
            result = result + ' ' + self.getKssUIDClass()

        return result
