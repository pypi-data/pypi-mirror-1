=============================
gocept Link Monitoring Server
=============================

The Link Monitoring Server (LMS) is a coherent set of components to regularly
check whether given URLs are reachable. It currently supports HTTP, HTTPS and
FTP URLs.


History
=======

gocept.lms is the third version of LMS (hence the major version number of
3.x).

The first version was directly integrated into CMFLinkChecker and ran as a
thread.  This was not very stable.

The second version used the Twisted framework and a MySQL database. This was
not very stable either.

The third version now is written in Zope 3/Grok, uses the ZODB as data
storage and separates concerns wherever possible. This is stable.


Components
==========

The LMS consists of small components that only communicate via storing data in
the ZODB.

XML-RPC server
++++++++++++++

The XML-RPC server provides the API to talk to the LMS from
applications/clients that want to have their URLs checked. It provides
operations to register and unregister clients and URLs.

A management system can register clients. A client can register URLs it wants
to be checked.

Scheduler
+++++++++

The scheduler looks over the age of the data from URLs that where added by the
clients. It decides when a URL needs to be checked and inserts it into the
check queue accordingly.


Checker
+++++++

The checker pulls URLs from the check queue and performs the actual check. It
has measures in place that limit the number of checks performed in parallel
and to avoid pounding too hard on external systems. (Per default it checks up
to 20 URLs at the same time and assures that URLs that belong to the same host
are checked at most once per second).

Notifier
++++++++

The notifier keeps the registered clients updated about the state information
for the URLs they subscribed to. Clients are notified via XML-RPC.

Synchroniser/Syncer
+++++++++++++++++++

The syncer is responsible for keeping the URL databases of the LMS and its
clients synchronized. It does this by regularly getting a full snapshot of the
clients' databases and provides them with the current status information for
all URLs they are interested in.


Installation
============

The installation works using a buildout. An example can be found at our SVN::

    % svn co http://svn.gocept.com/repos/gocept/gocept.lms/deployment/profiles

The buildout currently defines two profiles:

- `prod.cfg` for a production setup
- `test.cfg` for a test setup

The profiles are not really different right now, though. They're there to
illustrate the possibilities. The test profile looks like this::

    [buildout]
    extends = base.cfg

    [app]
    admin-password = admin
    appname = test
    mail-server-host = localhost

    [zeo]
    address = localhost:8100

    [lms]
    address = localhost:8080


To select the test profile create a `buildout.cfg` which includes it::

    [buildout]
    extends = profiles/test.cfg

Next, bootstrap the buildout with Python 2.5::

    % python2.5 bootstrap.py

This creates the actual buildout script as ``bin/buildout``::

    % bin/buildout

Running the buildout created a set of scripts, corresponding to the various
components.  The test profile uses a deployment sandbox, so all the scripts
are contained in ``parts/deployment/etc/init.d``::

    % ls parts/deployment/etc/init.d/
    lms-checker
    lms-notifier
    lms-scheduler
    lms-syncer
    lms-web
    lms-zeo

To get started, first start the ZEO and the LMS web interface::

    % parts/deployment/etc/init.d/lms-zeo start
    % parts/deployment/etc/init.d/lms-web start

Point your browser to http://localhost:8080. This opens the grok admin UI.
Create an LMS with the id ``test``. Once created, the LMS will display
"Congratulations". 


Start the other services now::

    % parts/deployment/etc/init.d/lms-checker start
    % parts/deployment/etc/init.d/lms-notifier start
    % parts/deployment/etc/init.d/lms-scheduler start
    % parts/deployment/etc/init.d/lms-syncer start


The next step is to register a client. The LMS welcome page has a link to a
very rudimentary form. There you have to enter the following data:

Client Id
    This is an identifier for the client. It is used in combination with the
    password to authenticate XML-RPC requests.

Password
    The password to authenticate the client.

Contact name
    Emails sent by the LMS will contain the name to address the recipient.

Contact email address
    Emails sent by the LMS regarding this client will be sent to this address.

Callback URL
    The callback URL is the XML-RPC point where the callback methods are
    invoked. For a gocept.linkchecker installation this would be
    http://example.com/portal_linkchecker/database/.

After registering the client, you can configure `gocept.linkchecker` (or any other
client) to talk to the LMS.
