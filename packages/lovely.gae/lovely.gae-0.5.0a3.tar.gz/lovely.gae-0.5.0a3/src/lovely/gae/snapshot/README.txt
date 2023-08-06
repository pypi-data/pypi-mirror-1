===============================
Snapshots of GAE Datastore Data
===============================

It is possible to create snapshots of pre-defined kinds. Snapshots are
created asynchrounously.

    >>> from lovely.gae.snapshot import api

    >>> import tempfile, os
    >>> s1 = api.create_snapshot(['Dummy'])
    >>> s1
    <lovely.gae.snapshot.models.Snapshot object at ...>

    >>> s1.status == s1.STATUS_STARTED
    True
    >>> from lovely.gae.async import get_tasks

The first task that is created is the batch task. This collects the
markers for the snapshot.

    >>> run_tasks()
    1

The callback is another task, that sets the markers.

    >>> run_tasks()
    1

    >>> from google.appengine.ext import db
    >>> s1 = db.get(s1.key())
    >>> s1.status == s1.STATUS_STORING
    True

Markers are stored on the snapshot as a dictionary of kind to
markers. We actually have no dummy objects present, so the markers are
empty.

    >>> s1.markers
    {'Dummy': []}

We now should have one job for the whole range of markers.

    >>> run_tasks()
    1

Let us now have a look at the status, which should be finished.

    >>> s1 = db.get(s1.key())
    >>> s1.status == s1.STATUS_FINISHED
    True

Let us do another snapshot with some actual objects in it.

    >>> class Dummy(db.Model):
    ...     title = db.StringProperty()
    >>> class Yummy(db.Model):
    ...     title = db.StringProperty()

    >>> for i in range(220):
    ...     d = Dummy(title=str(i))
    ...     k=d.put()
    ...     y = Yummy(title=str(i))
    ...     k=y.put()

If we specify no kind on snapshot creation any available kinds are snapshotted.

    >>> s2 = api.create_snapshot()
    >>> s2.kinds
    ['Dummy', 'Yummy']

We have 8 tasks to run

- create_ranges 2 times (1 for eache kind)
- 2 tines callback of create_ranges
- 2x2 times backup range store because > 200

    >>> run_tasks(recursive=True)
    8

Now there should be backkup range instances and one marker for each kind.

    >>> from pprint import pprint
    >>> s2 = db.get(s2.key())
    >>> len(s2.markers['Dummy'])
    1
    >>> len(s2.markers['Yummy'])
    1
    >>> s2.rangebackup_set.count()
    4

Note that backups are compressed using bz2, so the data is pretty
small. The key names of rangebackup entities contain the id of the
snapshot, its kind, position and size.

    >>> for rb in s2.rangebackup_set:
    ...     print rb.key().name()
    RB:442:Dummy:0000000000:1081
    RB:442:Dummy:0000000001:283
    RB:442:Yummy:0000000000:1108
    RB:442:Yummy:0000000001:283

Restoring
=========

We restore snapshot 1, which actually means we delete all "Dummy"
objects because this is the only kind in s1. The "Yummy" objects are
kept.

    >>> s1.restore()

    >>> run_tasks(recursive=True)
    1

    >>> Dummy.all().count()
    0
    >>> Yummy.all().count()
    220

Let us restore s2.

    >>> s2.restore()
    >>> run_tasks(recursive=True)
    4
    >>> Dummy.all().count()
    220
    >>> Yummy.all().count()
    220

Deleting
========

Whe delete is called on a snapshot the range backup objects also get
deleted.

    >>> from lovely.gae.snapshot import models
    >>> s2k = s2.key()
    >>> s2.delete()
    >>> models.RangeBackup.all().filter('snapshot', s2k).count()
    0

Creating Snapshots via http
===========================

For testing we setup a wsgi application.

    >>> from webtest import TestApp
    >>> from lovely.gae.snapshot import getApp
    >>> app = TestApp(getApp())

We can now create a snapshot via this url::

    >>> res = app.get('/lovely.gae/snapshot.CreateSnapshotHandler')
    >>> res.status
    '200 OK'
    >>> print res.body
    Created Snapshot 443
    Kinds: ['Dummy', 'Yummy']

Kinds are specified via query string.

    >>> res = app.get('/lovely.gae/snapshot.CreateSnapshotHandler?kinds=Yummy')
    >>> res.status
    '200 OK'
    >>> print res.body
    Created Snapshot 444
    Kinds: [u'Yummy']

    >>> res = app.get('/lovely.gae/snapshot.CreateSnapshotHandler?kinds=Yummy&kinds=Dummy')
    >>> res.status
    '200 OK'
    >>> print res.body
    Created Snapshot 445
    Kinds: [u'Yummy', u'Dummy']

Let us complete all jobs.

    >>> run_tasks(recursive=True)
    20

Downloading Snapshots
=====================

Snapshots can be downloaded as a single file, which then can be used
directly as a development datastore file.

Downloads are done with a client script that uses the remote api to
fetch the data. We just test the actual method that get's called
here.

    >>> from lovely.gae.snapshot import client
    >>> import tempfile, shutil, os
    >>> tmp = tempfile.mkdtemp()
    >>> f445 = client.download_snapshot(tmp)
    Downloading snapshot: 445
    Downloading RB:445:Dummy:0000000000:1081 pos: 1/4 remaining: 4.0 seconds
    Downloading RB:445:Dummy:0000000001:283 pos: 2/4 remaining: ... seconds
    Downloading RB:445:Yummy:0000000000:1108 pos: 3/4 remaining: ... seconds
    Downloading RB:445:Yummy:0000000001:283 pos: 4/4 remaining: ... seconds
    Saving to ...snapshot.445
    >>> os.listdir(tmp)
    ['snapshot.445']

By default the latest snapshot gets downloaded, but we can also
specify the id of the snapshot to fetch.

    >>> file_name = client.download_snapshot(tmp, 443)
    Downloading snapshot: 443
    Downloading RB:443:Dummy:0000000000:...
    Downloading RB:443:Dummy:0000000001:...
    Downloading RB:443:Yummy:0000000000:...
    Downloading RB:443:Yummy:0000000001:...
    Saving to .../snapshot.443
    >>> os.listdir(tmp)
    ['snapshot.443', 'snapshot.445']

If the file already exists we get an exception.

    >>> ignored = client.download_snapshot(tmp, 443)
    Traceback (most recent call last):
    ...
    RuntimeError: Out file exists '.../snapshot.443'


Let us test if the file works.

    >>> from google.appengine.api.datastore_file_stub import DatastoreFileStub
    >>> dfs = DatastoreFileStub('lovely-gae-testing',
    ...                         f445, None)
    >>> sum(map(len, dfs._DatastoreFileStub__entities.values()))
    440
