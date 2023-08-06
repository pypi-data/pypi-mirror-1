import logging
import os
import subprocess
import time

import paramiko

import cloudpool.environment as EnvironmentModule

class LocalShell(EnvironmentModule.Environment):

    DEFAULT_COMMANDBUILDER_TYPE = 'shell process'
    
    def execute(self, task, *args, **kargs):

        request = task.workRequest()
        
        commandBuilder = self.getCommandBuilder(task)

        command = commandBuilder.buildCommand(task)

        request.kwds['executed command'] = command
        
        logging.debug('%s executing command "%s"' % (self.__class__, command))
        processObj = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        request.kwds['process message output'] = processObj.stdout
        
        returnValue = processObj.wait()
        
        if returnValue is not 0:
            logging.error('%s exited with return code %s' % (command, returnValue))
            raise subprocess.CalledProcessError(returnValue, command)
        
        return returnValue
    
    # END class LocalShell
    pass


class RemoteShell(EnvironmentModule.Environment):

    DEFAULT_COMMANDBUILDER_TYPE = 'shell process'
    
    def __init__(self):
        
        # default stage root to root
        self.stageRoot([''])
        return

    def stageRoot(self, value=None):
        if value is not None:
            self._stageRoot = value
        if not hasattr(self, '_stageRoot'):
            self._stageRoot = None
        return self._stageRoot

    def connection(self):
        if not self.hasEstablishedConnection():
            connection = self.establishConnection()
            self._connection = connection
        return self._connection

    
    def disconnect(self):
        if not self.hasEstablishedConnection():
            return
        self.connection().close()
        return
    
    # END class RemoteShell
    pass


class SecureShell(RemoteShell):
    
    DEFAULT_COMMANDBUILDER_TYPE = 'shell process'
    
    def hasEstablishedConnection(self):
        if not hasattr(self, '_connection'):
            return False

        connection = self._connection
        if connection is None:
            return False
        if connection._transport is None:
            return False
        if not connection._transport.is_active():
            return False
        
        # TODO:
        # Should we also attempt to determine if the connection
        # has been authenticated as well?
        
        return True

    def hostname(self, value=None):
        if value is not None:
            self._hostname = value
        if not hasattr(self, '_hostname'):
            self._hostname = None
        return self._hostname

    def user(self, value=None):
        if value is not None:
            self._user = value
        if not hasattr(self, '_user'):
            self._user = None
        return self._user

    def keyfile(self, value=None):
        if value is not None:
            self._keyfile = value
        if not hasattr(self, '_keyfile'):
            self._keyfile = None
        return self._keyfile

    
    def establishConnection(self):
        keyfile = self.keyfile()
        pkey = paramiko.RSAKey.from_private_key_file(keyfile)

        connection = paramiko.SSHClient()
        connection._policy = paramiko.AutoAddPolicy()
        connection.connect(
            self.hostname(), 
            username=self.user(), 
            key_filename=self.keyfile()
        )
        return connection

    
    def getFS(self):
        return self.connection().open_sftp()

    
    def execute(self, task, *args, **kargs):
        
        # stage the input files if necessary
        task.stageInputFiles()
        
        # stage the executable if necessary
        task.stageExecutable()

        commandBuilder = self.getCommandBuilder(task)
        
        commandAsList = commandBuilder.buildCommand(task)

        command = ' '.join(commandAsList)
        
        returnValue = self.executeCommand(command)
        if returnValue is not 0:
            logging.error('%s exited with return code %s' % (command, returnValue))
            raise subprocess.CalledProcessError(returnValue, command)
        
        # de-stage the output files if necessary
        task.stageOutputFiles()
        
        return returnValue

    def executeCommand(self, command):
        logging.debug('%s executing command "%s"' % (self.__class__, command))

        client = self.connection()
        channel = client.get_transport().open_session()
        channel.exec_command(command)
        
        # sleep until the command exits
        while not channel.exit_status_ready():
            
            # TODO:
            # capture stdout and stderr as well
            
            time.sleep(1)
            pass
        returnValue = channel.recv_exit_status()
        return returnValue
    
    def getStagedPath(self, fileToStage):

        # TODO:
        # now flatten into a single list of strings
        # this needs to be less of a hack
        if isinstance(fileToStage, list):
            fullPath = self.stageRoot() + fileToStage
        else:
            fullPath = self.stageRoot() + [fileToStage]

        # TODO:
        # this actually needs to be the os.path.sep 
        # on the remote host
        return os.path.sep.join(fullPath)

    
    def setFilePermissions(self, remotefile=None, permissions=None):
        fs = self.getFS()
        fs.chmod(remotefile, permissions)
        return

    def constructPaths(self, file=None):
        # need to handle the case where file could be a list
        if isinstance(file, list):
            localpath = os.path.sep.join(file)
        else:
            localpath = file
        remotepath = self.getStagedPath(file)
        return localpath, remotepath

    def stageFile(self, file=None, **kwd):

        fs = self.getFS()

        localpath, remotepath = self.constructPaths(file=file)
        
        # first ensure that the directory exists
        try:
            fs.stat(remotepath)
        except IOError, e:
            remoteDir = remotepath.rsplit(os.path.sep, 1)[0]
            
            # cannot seem to get the following working
            # so calling executeCommand to create the directory instead
            # of course, the command only works on unix systems
            # fs.mkdir(remoteDir, mode=755)
            returnValue = self.executeCommand('mkdir -p %s' % remoteDir)
            if returnValue is not 0:
                raise NotImplementedError('creating directory for target staged file %s' % remotepath)
            pass
        
        # need to handle the case that localpath
        # is stored as a list
        fs.put(localpath, remotepath)
        
        return

    def destageFile(self, file=None, **kwd):

        fs = self.getFS()
        
        localpath, remotepath = self.constructPaths(file=file)

        fs.get(remotepath, localpath)
        
        return
    
    
    # END class SecureShell
    pass

