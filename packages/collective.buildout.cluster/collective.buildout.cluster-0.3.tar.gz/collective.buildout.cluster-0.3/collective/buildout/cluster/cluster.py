# Pull Zope configuration from .installed.cfg.
# It's a convenient place to get all the data
# for a buildout configuration because all the
# buildout variables are expanded already.

import os
import sys
import operator
import subprocess

WIN32 = sys.platform == 'win32'
if WIN32:
    # Always import pywintypes first thing so that the DLLs are
    # correctly located.
    import pywintypes
    import pythoncom

from iniparse import INIConfig
from iniparse import ConfigParser
from cStringIO import StringIO

from collective.buildout.cluster.server import ZEOServer
from collective.buildout.cluster.client import ZEOClient
from collective.buildout.cluster.async import Popen, send_all, recv_some

def normdrive(path):
    # Normalize drive letter to same case as getcwd() (which is
    # what buildout uses) otherwise we might run buildout with a
    # lowercase drive letter and then if ran manually, an
    # uppercase drive letter is returned and buildout considers
    # everything that has a generated path as modified.
    drive, path = os.path.splitdrive(path)
    drive = drive.upper()
    path = os.path.join(drive, path)
    return path

class Cluster(object):
    """ Well maybe not a cluster but I couldn't think of a better word
     currently a cluster contains zero or more ZEO servers and zero
     to or more ZEO clients. This forms our "cluster".
     """

    ZEOClientFactory = ZEOClient
    ZEOServerFactory = ZEOServer

    def __init__(self, path='.', 
                 config_file=None,
                 installed_file=None):
        self.reload = 1
        if os.path.isfile(path) and config_file is None and installed_file is None:
            # The buildout.cfg file was passed as the one and only
            # argument.
            config_file = os.path.basename(path)
            path = os.path.dirname(path)

        path = normdrive(path)

        if config_file is None:
            config_file = 'buildout.cfg'
        else:
            config_file = normdrive(config_file)
            
        if not os.path.isabs(config_file):
            config_file = os.path.realpath(os.path.join(path, config_file))

        if installed_file is None:
            installed_file = '.installed.cfg'
        else:
            installed_file = normdrive(installed_file)

        if not os.path.isabs(installed_file):
            installed_file = os.path.realpath(os.path.join(path, installed_file))

        self.path = path
        self.config_file = config_file
        self.installed_file = installed_file
        self.load()

    def __getitem__(self, name):
        class Section(object):
            def __init__(self, config, name):
                self.config = config
                self.name = name
            def __getitem__(self, name):
                return self.config.get(self.name, name, None)
        return Section(self.config, name)

    def checkPorts(self):
        raise NotImplementedError()

        ports = {}
        conflicts = []
        for client in self.clients:
            enabled = dict(client.getPortsEnabled())
            for pn in client_portsList:
                if not enabled.get(pn):
                    continue
                p = client.getPort(pn)
                if not p or pn in ("ZEO_SERVER_HOST", "ZEO_SERVER_PORT"):
                    if (pn == "ZEO_SERVER_PORT" and
                        client.getPort("ZEO_SERVER_HOST") == 'localhost'):
                        pass
                    else:
                        continue
                if ports.get(p) and not pn in ('ZEO_SERVER_PORT',):
                    if p not in conflicts:
                        conflicts.append(
                            {'port':p,
                             'first':{'portName': pn,
                                       'client': client.getDescription()},
                             'other': ports[p],
                             })
                else:
                    ports[p] = {'portName':pn, 
                                'client':client.getDescription()}

        return conflicts

    def addNewClient(self, name, settings=None):
        if settings is None:
            settings = {}

        cfg_file = open(self.config_file, 'rb')
        try:
            cfg = INIConfig(cfg_file)
        finally:
            cfg_file.close()

        try:
            section = cfg[name]
            raise ValueError('A section named %r already exists!' % name)
        except KeyError:
            pass

        # Add a new section for the new client, using the zope2cluster
        # recipe
        setattr(getattr(cfg, name), 'recipe', 'collective.recipe.zope2cluster')

        # If any extra settings were passed on, use them for the new
        # section.
        if settings is not None:
            for key, value in sorted(settings.items()):
                setattr(getattr(cfg, name), key, value)

        # Finally, append to the 'parts' section so that it's picked
        # up by buildout.
        parts = cfg['buildout']['parts'].split('\n')
        clean = [p.strip() for p in parts]
        clients = self.getClientNames()[:]

        # Insert after the last client while keeping identation, if
        # clients exist.
        found = False
        while clients:
            last_client = clients.pop()
            if last_client in clean:
                idx = clean.index(last_client)
                last = parts[idx]
                parts.insert(idx + 1, last.replace(last_client, name))
                found = True
                break

        if not found:
            # Otherwise, append after the last part (while still
            # keeping the indentation) since we don't know what
            # dependencies we might need.
            parts.append(parts[-1].replace(parts[-1].strip(), name))

        setattr(getattr(cfg, 'buildout'), 'parts', '\n'.join(parts))

        fp = open(self.config_file, 'wb')
        try:
            fp.write(str(cfg).strip() + os.linesep)
        finally:
            fp.close()
        
        # Hardcoded location to the expected defaults. It's unlikely
        # that this will ever change, and we don't want to run
        # buildout *just* to get this path right.
        settings['location'] = os.path.join(
            os.path.dirname(self.config_file), 'parts', name)

        settings['name'] = name
        client = self.ZEOClientFactory(settings.copy(), self)
        self.registerClient(client)

        return client

    def removeClient(self, name):
        cfg_file = open(self.config_file, 'rb')
        try:
            cfg = INIConfig(cfg_file)
        finally:
            cfg_file.close()

        try:
            del cfg[name]
        except KeyError:
            pass
        
        # Finally, remove from the 'parts' section so that it's
        # removed from the buildout.
        parts = cfg['buildout']['parts'].split('\n')
        clean = [p.strip() for p in parts]
        clients = self.getClientNames()[:]

        # Insert after the last client while keeping identation, if
        # clients exist.
        if name in clients and name in clean:
            del parts[clean.index(name)]
            del self.clients[name]

        setattr(getattr(cfg, 'buildout'), 'parts', '\n'.join(parts))

        fp = open(self.config_file, 'wb')
        try:
            fp.write(str(cfg).strip() + os.linesep)
        finally:
            fp.close()

    def getClient(self, name):
        return self.clients[name]

    def getServer(self, name):
        return self.servers[name]

    def registerClient(self, client):
        self.clients[client['name']] = client

    def registerServer(self, server):
        self.servers[server['name']] = server

    def getClients(self):
        return [c for n, c in sorted(self.clients.iteritems())]

    def getServers(self):
        return [s for n, s in sorted(self.servers.iteritems())]

    def getClientNames(self):
        return sorted(self.clients.keys())

    def getServerNames(self):
        return sorted(self.server.keys())

    def getStatus(self):
        status = {}
        status['servers'] = [(s, s.getStatus()) for s in self.getServers()]
        status['clients'] = [(c, c.getStatus()) for c in self.getClients()]
        return status

    def save(self):
        raise NotImplementedError()

    def load(self):
        if self.reload:
            self.clients = {}
            self.servers = {}

            self.original = original = ConfigParser()
            self.config = config = ConfigParser()
            print "cwd: %s" % os.getcwd()
            print "Loading config file: %s" % self.config_file
            print "Loading installed file: %s" % self.installed_file
            original.read(self.config_file)
            config.read(self.installed_file)
            print "Sections found: %s" % config.sections()

            # find first zope2 instance
            cluster_clients = []
            for section in original.sections():
                options = {}
                if not original.has_option(section, 'recipe'):
                    continue

                recipe = original.get(section, 'recipe') 
                if recipe == 'plone.recipe.zope2instance':
                    factory = self.ZEOClientFactory
                    register = self.registerClient
                elif recipe == 'collective.recipe.zope2cluster':
                    factory = self.ZEOClientFactory
                    def register(client):
                        self.registerClient(client)
                        cluster_clients.append(client)
                elif recipe == 'plone.recipe.zope2zeoserver':
                    factory = self.ZEOServerFactory
                    register = self.registerServer
                else:
                    continue

                options['name'] = section
                for cfg in (original, config):
                    # We merge the information from both files, in
                    # order to get a better overview of what's
                    # installed. Note that original comes first, so
                    # whatever is installed overrides a possibly
                    # different value from installed.
                    try:
                        for opt in cfg.options(section):
                            try:
                                options[opt] = cfg.get(section, opt)
                            except:
                                # we can't interpolate buildout % vars
                                continue
                    except:
                        # If the section doesn't exist in one of the
                        # files (which might be true if it was added
                        # to original but not installed yet, just
                        # continue.
                        continue
                register(factory(options, self))

            for client in cluster_clients:
                client.setDefaults(self.getClient(client['instance-clone']))

            self.reload = 0

    def buildout(self, offline=True, newest=False, extra=None, verbose=2):
        cmd = [os.path.join(self.path, 'bin', 'buildout')]
        args = ['-c',
                self.config_file]
        if offline:
            args.append('-o')
        else:
            args.append('-O')
        if newest:
            args.append('-n')
        else:
            args.append('-N')
        if verbose:
            args.extend(verbose * ['-v'])
        if extra:
            args.extend(extra)

        if sys.platform == 'win32':
            shell, tail = ('cmd', '\r\n')
        else:
            shell, tail = ('sh', '\n')

        print cmd, args
        kw = dict(stdin=subprocess.PIPE,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE)
        
        if sys.platform == 'win32':
            import win32process
            kw['creationflags'] = win32process.CREATE_NO_WINDOW

        process = Popen(cmd + args, **kw)
        stdout, stderr = StringIO(), StringIO()
        
        while True:
            output = recv_some(process, t=5.0, e=0)
            if not output:
                break
            stdout.write(output)
            print output

        while True:
            output = recv_some(process, t=5.0, e=0, stderr=1)
            if not output:
                break
            stderr.write(output)
            print output

        process.wait()
        return stdout.getvalue(), stderr.getvalue(), process.returncode


def ClusterStop(items):
    for item in items:
        if WIN32 and not item.isServiceInstalled():
            continue
        if item.isRunning():
            item.stop()

def ClusterStart(items):
    ClusterInstall(items)
    for item in reversed(items):
        if WIN32 and not item.isServiceInstalled():
            continue
        if not item.isRunning():
            item.start()

def ClusterInstall(items, start_type="auto"):
    for item in reversed(items):
        if WIN32 and not item.isServiceInstalled():
            item.install(start_type=start_type)

def ClusterRemove(items):
    ClusterStop(items)
    for item in items:
        if WIN32 and item.isServiceInstalled():
            item.remove()

def main():
    import optparse
    parser = optparse.OptionParser(usage = "%prog [options] command ...")
    parser.add_option("-c", "--cfg-file",
                      help="""Cluster configuration file""")

    options, args = parser.parse_args()
    
    if not args:
        parser.error("No command specified")
    if not options.cfg_file:
        parser.error("Configuration file is required (--cfg-file)")
        
    cluster = Cluster(path=options.cfg_file)
    items = [item for item in cluster.getClients() + cluster.getServers()
             if item.exists()]

    for arg in args:
        if arg == "remove":
            ClusterRemove(items)
        elif arg == "stop":
            ClusterStop(items)
        elif arg == "install":
            start_type = "auto"
            if "manual" in args:
                start_type = "manual"
            ClusterInstall(items, start_type)
        elif arg == "start":
            ClusterStart(items)

