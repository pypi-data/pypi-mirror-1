from kss.core import KSSView

class ActionsView(KSSView):

    def toggleClass(self):
        core = self.getCommandSet('core')
        selector = core.getSameNodeSelector()
        core.toggleClass(selector, 'selected')
        return self.render()

    def focus(self, id):
        self.getCommandSet('core').focus('#' + id)
        return self.render()

    def addClass(self):
        core = self.getCommandSet('core')
        selector = core.getSameNodeSelector()
        core.addClass(selector, 'selected')
        return self.render()

    def removeClass(self):
        core = self.getCommandSet('core')
        selector = core.getSameNodeSelector()
        core.removeClass(selector, 'selected')
        return self.render()
