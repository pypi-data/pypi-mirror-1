from kss.core.kssview import CommandSet

class JWPlayerCommands(CommandSet):

    # Add your own commands here, you can use the following code as
    #  a starting point
    def enableJWPlayer(self, selector, data):
        command = self.commands.addCommand('enableJWPlayer', selector)
        # Repeat for each parameter you need
        #command.addParam('parameter', data)
