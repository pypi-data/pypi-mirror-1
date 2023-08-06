Example usage
=============

We'll start by creating a buildout that contains a base ZEO Client, a
'cluster' ZEO Client and two ZEO Servers::

    >>> write('buildout.cfg',
    ... r"""
    ... [buildout]
    ... parts = 
    ...    instance-1
    ...    instance-2
    ...    server-1
    ...    server-2
    ...
    ... [instance-1]
    ... http-address = 8080
    ... recipe = plone.recipe.zope2instance
    ... zeo-address = 8100
    ... zeo-client = on
    ...
    ... [instance-2]
    ... recipe = collective.recipe.zope2cluster
    ... http-address = 8081
    ... instance-clone = instance-1
    ... 
    ... [server-1]
    ... recipe = plone.recipe.zope2zeoserver
    ... zeo-address = 8100
    ... 
    ... [server-2]
    ... recipe = plone.recipe.zope2zeoserver
    ... zeo-address = 8101
    ... """)

    >>> write('.installed.cfg',
    ... r"""
    ... [instance-1]
    ... bin-directory = C:\src\server-buildout\5.0\bin
    ... http-address = 8080
    ... location = C:\src\server-buildout\5.0\parts\instance-1
    ... recipe = plone.recipe.zope2instance
    ... zeo-address = 8100
    ... zeo-client = on
    ... zope2-location = C:\src\server-buildout\5.0\parts\zope2
    ...
    ... [instance-2]
    ... http-address = 8081
    ... location = C:\src\server-buildout\5.0\parts\instance-2
    ... recipe = collective.recipe.zope2cluster
    ... instance-clone = instance-1
    ... zope2-location = C:\src\server-buildout\5.0\parts\zope2
    ... 
    ... [server-1]
    ... location = C:\src\server-buildout\5.0\parts\server-1
    ... bin-directory = C:\src\server-buildout\5.0\bin
    ... recipe = plone.recipe.zope2zeoserver
    ... zeo-address = 8100
    ... zope2-location = C:\src\server-buildout\5.0\parts\zope2
    ... 
    ... [server-2]
    ... location = C:\src\server-buildout\5.0\parts\server-2
    ... bin-directory = C:\src\server-buildout\5.0\bin
    ... recipe = plone.recipe.zope2zeoserver
    ... zeo-address = 8101
    ... zope2-location = C:\src\server-buildout\5.0\parts\zope2
    ... """)

Reading the cluster configuration from those files should list two
servers and two client instances::

    >>> import os
    >>> from collective.buildout.cluster.cluster import Cluster

    >>> cluster = Cluster(os.getcwd(), 'buildout.cfg', '.installed.cfg')
    cwd: ...

    >>> for server in cluster.getServers():
    ...     print server.getInstanceName()
    ...     print server.getInstanceCtl()
    ...     print server.getPort('zeo')
    ...     print
    server-1
    C:\src\server-buildout\5.0\bin\server-1
    8100
    <BLANKLINE>
    server-2
    C:\src\server-buildout\5.0\bin\server-2
    8101
    <BLANKLINE>

    >>> for client in cluster.getClients():
    ...     print client.getInstanceName()
    ...     print client.getInstanceCtl()
    ...     print client.getPort('http')
    ...     print
    instance-1
    C:\src\server-buildout\5.0\bin\instance-1
    8080
    <BLANKLINE>
    instance-2
    C:\src\server-buildout\5.0\bin\instance-2
    8081
    <BLANKLINE>

Now, let's add a third client and make sure the ``buildout.cfg`` file
was changed accordingly::

    >>> settings = {'instance-clone': 'instance-1',
    ...             'http-address': '8082'}

    >>> client = cluster.addNewClient('instance-3', settings=settings)

    >>> cat('buildout.cfg')
    <BLANKLINE>
    ...
    parts =
       instance-1
       instance-2
       instance-3
       server-1
    ...
    [instance-3]
    recipe = collective.recipe.zope2cluster
    http-address = 8082
    instance-clone = instance-1

    >>> client['http-address']
    '8082'

    >>> client['instance-clone']
    'instance-1'

    >>> client['name']
    'instance-3'

Trying to add another client by the same name should fail::

    >>> cluster.addNewClient('instance-3', settings=settings)
    Traceback (most recent call last):
    ...
    ValueError: A section named 'instance-3' already exists!

Changing a port number, or even enabling a port should be possible::

    >>> i2 = cluster.getClient('instance-2')
    >>> i2.setPort('http', '8091')

    >>> i2['http-address']
    '8091'

    >>> i2.setPort('webdav', '8092')

    >>> i2['webdav-address']
    '8092'

    >>> cat('buildout.cfg')
    <BLANKLINE>
    ...
    [instance-2]
    recipe = collective.recipe.zope2cluster
    http-address = 8091
    instance-clone = instance-1
    webdav-address = 8092
    ...

So should disabling a port (by setting it to ``None``)::

    >>> i2.setPort('webdav', None)

    >>> cat('buildout.cfg')
    <BLANKLINE>
    ...
    [instance-2]
    recipe = collective.recipe.zope2cluster
    http-address = 8091
    instance-clone = instance-1
    ...

    >>> i2['webdav-address']
    Traceback (most recent call last):
    ...
    KeyError: 'webdav-address'

Finally, deleting a client should be possible as well::

    >>> for client in cluster.getClients():
    ...     print client.getInstanceName()
    instance-1
    instance-2
    instance-3

    >>> cluster.removeClient('instance-3')

    >>> cat('buildout.cfg')
    <BLANKLINE>
    ...
    parts =
       instance-1
       instance-2
       server-1
    ...

    >>> for client in cluster.getClients():
    ...     print client.getInstanceName()
    instance-1
    instance-2
