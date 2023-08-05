from interfaces import IScriptaculousEffectsCommands
from kss.core.azaxview import CommandSet

class ScriptaculousEffectsCommands(CommandSet):

    def effect(self, selector, type):
        """ see interfaces.py """
        command = self.commands.addCommand('effect', selector)
        data = command.addParam('type', type)

