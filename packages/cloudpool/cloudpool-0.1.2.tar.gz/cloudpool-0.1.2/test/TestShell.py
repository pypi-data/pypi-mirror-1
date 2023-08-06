from __future__ import with_statement

import os
import unittest

import simplejson as ConfigModule

import cloudpool.shell as ShellModule

class TestSecureShell(unittest.TestCase):

    @staticmethod
    def loadCredentials():

        configFilePath = os.path.join(
            os.getcwd(), 'test', 'config')

        with open(configFilePath) as f:

            config = ConfigModule.load(f)

            remoteExecuteCredentials = config['remote execute credentials']
            assert len(remoteExecuteCredentials), 'expected to find remote execute credentials'

            return remoteExecuteCredentials

        raise NotImplemented(
            'could not read credentials from config file %s' % configFilePath)




    @staticmethod
    def getShell():

        shell = ShellModule.SecureShell()
        # set the hostname, user, and keyfile

        credentials = TestSecureShell.loadCredentials()

        credential = credentials[0]

        hostname = credential['hostname']
        user = credential['user']
        keyfile = credential['keyfile']

        shell.hostname(hostname)
        shell.user(user)
        shell.keyfile(keyfile)

        return shell


    STAGE_ROOT = ['', 'tmp']

    def setUp(self):
        self.shell = TestSecureShell.getShell()
        self.shell.stageRoot(TestSecureShell.STAGE_ROOT)
        return

    def testConstructPaths(self):
        path = ['path', 'to', 'file']
        localpath, remotepath = self.shell.constructPaths(path)
        self.assertEquals(os.path.sep.join(path),
                          localpath)
        self.assertEquals(self.shell.getStagedPath(localpath),
                          remotepath)

        path = '/path/to/file'
        localpath, remotepath = self.shell.constructPaths(path)
        self.assertEquals(os.path.join(path),
                          localpath)
        self.assertEquals(self.shell.getStagedPath(localpath),
                          remotepath)

        return


    def testGetStagedPath(self):
        path = ['path', 'to', 'file']
        stagedPath = self.shell.getStagedPath(path)
        expected = os.path.sep.join(TestSecureShell.STAGE_ROOT + path)
        self.assertEquals(
            expected,
            stagedPath)

        path = os.path.sep.join(path)
        stagedPath = self.shell.getStagedPath(path)
        self.assertEquals(
            expected,
            stagedPath)

        return

    # END class TestSecureShell
    pass



