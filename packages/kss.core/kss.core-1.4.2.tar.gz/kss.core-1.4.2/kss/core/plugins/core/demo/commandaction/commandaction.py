from kss.core import KSSView

class ActionsView(KSSView):

    def toggleClass(self):
        core = self.getCommandSet('core')
        selector = core.getSameNodeSelector()
        core.toggleClass(selector, 'selected')
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
    
    #focus

    def focus(self, id):
        self.getCommandSet('core').focus('#' + id)
        return self.render()

    #action-cancel

    def toCancel(self):
        core = self.getCommandSet('core')
        core.insertHTMLAsLastChild('#logger', 'action')
        return self.render()

    #setKssAttribute

    def echo(self, value):
        core = self.getCommandSet('core')
        core.insertHTMLAsLastChild('#logger', value)
        return self.render()
    
    def setKssAttribute(self):
        core = self.getCommandSet('core')
        core.setKssAttribute('#command', 'name', 'value-from-command')
        return self.render()

