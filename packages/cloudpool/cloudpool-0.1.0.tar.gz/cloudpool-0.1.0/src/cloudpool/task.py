import logging

class CommandBuilder(object):

    def buildCommand(self, task):
        workRequest = task.workRequest()
        command = workRequest.kwds['command to execute']
        return command

    # END class CommandBuilder
    pass


class Task(object):

    def do(self, *args, **kwds):
        # environment = self.workRequest().kwds['execute environment']
        environment = self.getExecuteEnvironment()
        return environment.execute(self, *args, **kwds)

    
    def workRequest(self, value=None):
        if value is not None:
            self._workRequest = value
        if not hasattr(self, '_workRequest'):
            self._workRequest = None
        return self._workRequest

    
    def getCommandBuilder(self):
        executeEnv = self.getExecuteEnvironment()
        
        request = self.workRequest()

        commandBuilderMap = request.kwds['command builder map']

        # default to the one specified by the environment
        commandBuilderType = executeEnv.DEFAULT_COMMANDBUILDER_TYPE
        
        if hasattr(self, 'getCommandBuilderType') and \
           self.getCommandBuilderType() is not None:
            commandBuilderType = self.getCommandBuilderType()
            logging.debug("using task's command builder type")
            pass
        else:
            logging.debug("using execute environment's default command builder type")
            
        if not commandBuilderType in commandBuilderMap:
            raise KeyError('cannot retrieve command builder as none for %s specified' % commandBuilderType)
        
        commandBuilder = commandBuilderMap[commandBuilderType]

        logging.debug("retrieved %s for command builder type %s" % 
                      (commandBuilder, commandBuilderType))
            
            
        return commandBuilder
    
    
    def getExecuteEnvironment(self):
        request = self.workRequest()
        return request.kwds['execute environment']

    
    def stageExecutable(self):
        return

    def stageInputFiles(self):
        return

    def stageOutputFiles(self):
        return

    # END class Task
    pass
