import logging

class Environment(object):
    
    def execute(self, task, *args, **kargs):
        raise NotImplemented(
            'have not implemented execute() for %s' % self.__class__)
 
    def getCommandBuilder(self, task):
        return task.getCommandBuilder()
    
    # END class Environment
    pass


class PrintTaskCommand(Environment):
    
    DEFAULT_COMMANDBUILDER_TYPE = 'print task'
    
    def __init__(self):
        return
    
    def outputStream(self, value=None):
        if value is not None:
            self._outputStream = value
        if not hasattr(self, '_outputStream'):
            self._outputStream = None
        return self._outputStream

    def prefix(self, value=None):
        if value is not None:
            self._prefix = value
        if not hasattr(self, '_prefix'):
            self._prefix = None
        return self._prefix

    def postfix(self, value=None):
        if value is not None:
            self._postfix = value
        if not hasattr(self, '_postfix'):
            self._postfix = None
        return self._postfix

    def execute(self, task, *args, **kargs):
        
        commandBuilder = self.getCommandBuilder(task)
        
        command = commandBuilder.buildCommand(task)

        if self.prefix():
            self.outputStream().write(self.prefix())
        if self.outputStream():
            self.outputStream().write(' '.join(command))
        if self.postfix():
            self.outputStream().write(self.postfix())
        
        return 0
    
    # END class PrintTaskCommand
    pass


class PythonEval(Environment):

    DEFAULT_COMMANDBUILDER_TYPE = 'python eval'
    
    
    def execute(self, task, *args, **kargs):
        request = task.workRequest()
        
        commandBuilder = self.getCommandBuilder(task)

        command = commandBuilder.buildCommand(task)

        request.kwds['executed command'] = command
        
        logging.debug('%s executing command "%s"' % (self.__class__, command))
        evalResult = eval(command)

        request.kwds['eval result'] = evalResult
        
        return 0
    
    # END class PythonEval
    pass
