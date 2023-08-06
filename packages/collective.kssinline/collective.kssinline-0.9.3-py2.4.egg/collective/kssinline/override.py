from archetypes.kss.fields import ATFieldDecoratorView
from archetypes.kss.commands.validation import ValidationCommands
from Acquisition import aq_inner
import base64

class KssInlineATFieldDecoratorView(ATFieldDecoratorView):

    def getKssClasses(self, fieldname, templateId=None, macro=None, target=None):
        result = ATFieldDecoratorView.getKssClasses(self, fieldname, templateId, macro, target)        
        if result:
            # hedley: UID must be present to enable override of context.
            # This should happen in future versions of archetypes.kss / Archetypes.
            context = aq_inner(self.context)
            if context.isTemporary():
                # Abuse atuid to store path info
                attr = " kssattr-atuid-%s" % base64.b64encode('/'.join(context.getPhysicalPath()))
                result = result + attr
            else:
                result = result + ' ' + self.getKssUIDClass()

        return result
