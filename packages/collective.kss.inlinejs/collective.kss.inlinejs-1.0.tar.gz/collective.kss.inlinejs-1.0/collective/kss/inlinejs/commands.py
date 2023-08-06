from zope.interface import implements

from kss.core.kssview import CommandSet

from collective.kss.inlinejs.interfaces import IInlineJsCommands

class InlineJsCommands(CommandSet):
    implements(IInlineJsCommands)
    effect = 'inlinejs-effect'

    def execJs(self, selector, code, debug='0'):
        command = self.commands.addCommand(self.effect, selector)

        command.addParam('code', code)
        command.addParam('debug', debug)

