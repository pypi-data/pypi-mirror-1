from kss.core import KSSView

class ActionsView(KSSView):

    def toggleClass(self):
        self.getCommandSet('core').toggleClass('#toggleclass-button', 'selected')
        return self.render()

    def focus(self, id):
        self.getCommandSet('core').focus('#' + id)
        return self.render()
