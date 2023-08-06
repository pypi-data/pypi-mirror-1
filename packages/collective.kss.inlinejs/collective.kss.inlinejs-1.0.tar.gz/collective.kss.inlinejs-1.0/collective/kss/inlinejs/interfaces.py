from zope.interface import Interface

class IInlineJsCommands(Interface):
    """Inline js plugin for kss"""

    def execJs(selector, code, debug='0'):
        """You can pass a selector and the inline js code to be applied"""

