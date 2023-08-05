==============
ReleaseManager
==============


Introduction
============

Welcome to ReleaseManager!  What we've tried to produce with the release manager project is a simple, extensible way to manage complex environments.  This has grown out of our own need to manage a dozen or more code bases, each with unique build procedures, many of which produce resources that must be installed on four or more machines, for multiple environments (prod, dev, qa, etc).  The administrative overhead of managing so many applications, different permission levels to different environments for different groups, unique build and install environments, sometimes with more than one per piece of hardware, forced us to realize that there had to be a better way.

Background
==========

ReleaseManager consists of three primary components: the builder, the installer, and the manager.  The builder simply provides a unique set of build behaviors for a given host platform.  If you have a java application that must be checked out from subversion, compiled, built into a WAR file, perhaps have some ant build run, and then sent to a number of different machines, you simply provide a plugin that supports this kind of build.  The installer simply provides a set of install behaviors for specific targets.  The manager centralizes the ability to interact with broad sets of builders and installers without having to be aware of the entirety of the infrastructure.

Before going too much further, it is necessary to explain a few concepts that are core to the ReleaseManager infrastructure.  Below is a set of terms and explanations, to establish the vocabulary for the rest of the documenation.

NamedTarget
-----------
- A target for an install.  something like "webapp_container" or "apache_directory".
- Has an InstallBehavior that is built against a config.

InstallBehavior
---------------
- Install behaviors can do things like extract archives, move files, copy files, etc.
- Install behaviors are instantiated by a NamedTarget based on the environment against which it is running.
- Install behaviors more complicated than "unarchive" or "put file in place" are likely to need to be provided by the developer creating the installer instance, but is a fairly trivial activity.

Project
-------
- A project that can be built and installed.  For a J2EE application, think "static files", "webapp WAR file", and associated elements.
- Has a collection of NamedTargets of which it is composed.

Environment
-----------
- A meta-project grouping of applications and resources.  Think "prod", "dev", "qa", etc.

ReleaseManager
--------------
- A server aware of a set of NamedTargets, Projects, BuildHosts, and ReleaseDaemons.

BuildHost
---------
- A host able to build a certain set of Projects.
- Is able to register itself with multiple ReleaseManager instances, advertising Projects.

ReleaseDaemon
-------------
- A worker process able to install a subset of NamedTargets into specific environments.
- Is able to register itself with multiple ReleaseManager instances, advertising Environments and associated NamedTargets.


Infrastructure
==============

The real *win* for ReleaseManager is it's ability to be highly distributed and persistent.  When you create a manager instance, it has the ability to be configured to recognize an arbitrary assortment of projects.  Manager instances can be built on more than one machine, or on the same machine running on different ports, able to handle overlapping, or entirely segmented, sets of projects.  These manager instances can accept registrations from build hosts and installers that are both dedicated solely to the particular manager, or multiple manager instances in tandem.  Because of Twisted's Deferred architecture, managers can service an arbitrary number of requests for build and install at any time, limited only by the machine, disk, and network speeds available.  If you're installing three 200MB compressed applications to multiple remote hosts all at once, serviced from the same box, then certainly you may experience a bit of latency, but there will be no actual lock or bottleneck, no blocking calls from server or client.

The most simple way to work through the infrastructure, and its complexities, is simply to follow the path of a request through the system.  For the simplicity of the example, we will assume that we're using anonymous authentication, and that we have a manager, builder, and installer all created on the machine.

First and foremost, we fire up the manager instance.  Once installers and builders have been registered with a manager, the registrations will persist between manager instance stops and starts, but for the first run, the manager must be available.  Once the builder and installer are similarly started (all of these can be started simply by changing directory to the installation directory for each, and running python serve.py, or building a service-style script, etc), we will notice on the console (or in the log) of the manager that it has recieved registrations from both the installer and the builder.  On the console for each of these, it should indicate what it either knows how to build or what it knows how to install, and it will have passed this information along to the manager at registration time.

We should now have a manager, builder, and installer all ready and available.  We need then simply to connect to the manager via xmlrpc, and tell it what we intend to do.  All exposed calls in the ReleaseManager heirarchy have the following signature:

    remote.action(credentials, request_data)

Where credentials is an arbitrarily formated dictionary (Perl hash, Java Map/HashMap, Python dict, etc) containing elements like "username", "password", "realm", "role", and request_data is the actual structure of all arguments and parameters necessary for the particular action in question.

The following example, given in python, describes the behavior expected.  We'll go line by line afterwards.  Credentials is shown purely for example, since we've established that we'll be using anonymous authentication.

>>> from xmlrpclib import ServerProxy
>>> relman_url = "http://localhost:10000"
>>> relman = ServerProxy(relman_url)
>>> credentials = dict(username = 'relman_test', password = 'relman_test') 
>>> request_data = dict(project = 'template', trunk=True, action="install", env="test")
>>> trans_id = relman.request_action(credentials, request_data)
>>> relman.query_transaction(trans_id) # always the initial status 
'STARTED'
>>> relman.query_transaction(trans_id) # assuming build takes long enough for us to see this status
'BUILD_COMPLETED'
>>> relman.query_transaction(trans_id) # the final success status
'INSTALL_COMPLETED'

ReleaseManager, in order to implement non-blocking transactions for multiple hosts, utilizes a simple transaction system, where a request is registered, and a transaction id is returned to the requesting client.  The client can then query on that transaction, getting back a status each time indicating the progress of the request through the system.  The transaction id is also linked to the history table, so it is possible to, in the case of error or simple diagnostics, trace a transaction id through its history.

Step by step then, what is happening here?  As you can see, we connect to the manager instance on the configured port (default is 10000).  We construct a credentials dict, and a request data dict.  The request data dict, at its simplest, takes an indicated project, the action requested (build or install, unless your release manager has been extended), and the environment against which you intend the action to be accomplished (only necessary for install... build is not environment aware, again, unless your manager and builder have been extended), and some combination of svn-aware params, like trunk=True, or a branch, tag, revision, or specific url.

Our request is to install the "template" project from trunk into environment test.  This assumes a number of things, or the request will fail, and the failure will be logged.  The first is that the manager instance is aware of the "template" project.  What this means is that the manager has loaded the "template" project from a configuration file, and that project configuration file indicates what named targets are collected by this project designation.  It can be as simple as a single named target per project, though many projects will likely contain multiple named targets.  The second assumption is that there is a builder somewhere that has advertised that it knows how to build the project "template."  For the sake of discussion, we're assuming our setup has this configured (and if you installed ReleaseManager instances with relman_ctl, this assumption will be correct for you too, unless you've changed it since).  The third assumption is that at least one installer is advertizing the set of named targets that correspond to the project "template" in the environment "test".  Again, out of the box, this will be true.

Assuming, then, that all of these things are true, the path of the request is this:

The manager receives a request for install of "template" to "test".  The manager checks its registrations to determine if it has a builder registered that knows how to build "template."  If so, it then checks its registrations to determine if it has at least one installer that is advertizing the named targets (defined in the project) for "template" in the environment "test."  Assuming all of this is true, the manager forwards the request along to the builder.  

The builder receives the same credentials/request_data set that the manager original did from the client, modified slightly by the manager to keep each build and install set unique per request.  The builder then simply checks the project name, and, since it has advertised that it is able to build for the listed project, it simply looks up in its own registrations what build behavior it has associated with a particular project, and attempts to run the build for that project.  When the build has completed, it creates an file, containing other zipped resources and an index file that matches named target to the particular resource in the archive.  With this successfully completed, it sends the archive file across the xmlrpc session back to the manager, and cleans up its working directory.

Once the manager has this index-and-resource archive, it extracts it to a temporary directory, and looks through the index file.  It finds the named target to resource mapping, and matches these to the installers that it found before.  It then reads these files in and sends them across the new xmlrpc connection to the installer, indicating that it is for the requested environment, to the intended named targets.  To note, the manager will send these files to ALL installers that have registered as being available for the environment/named_target combination.  This is by design, to support multiple-host installs (think web-farm) out of the box, without extra configuration overhead.

Once the installer receives the file from the manager, it has a fairly simple job to do.  An install path has been configured per named target, and an install behavior has been registered.  It looks up its own registration of named targets, and finds the configured install behavior, and simply runs it against the resource.  In many cases, it will simply be unarchiving a file, or putting some file on to the filesystem somewhere.  Install behaviors can, in fact, be significantly more complex than this, but that behavior would be provided by the developer.

Assuming the installation is successful, the installer will respond to the manager, indicating success (or failure if not-so-successful), and the manager will update the status in the transaction table, so that as the client interrogates the transaction id, it will see the updated status.

That describes the whole of the process, as it relates to a simple request.

Usage
=====

There are two different aspects of usage for ReleaseManager.  We'll cover the simple and straightforward one first: installation.

ReleaseManager comes packaged with the relman_ctl utility.  It does the job of creating basic manager, builder, and installer installations.  Using it is simple enough.  The format of the command is:

relman_ctl generate [manager|builder|installer] <the name of your [manager|builder|installer]>

If you intended to install a builder named "my_test_builder", it would be like this:

$ relman_ctl generate builder my_test_builder

Same for installers and managers.  When you install a builder, you should find a layout similar to this:

Builder Installation Layout
---------------------------

.
|-- README.txt
|-- archive
|-- builder
|   |-- __init__.py
|   `-- template.py
|-- conf
|   `-- builder
|       |-- build_host_template.xml
|       `-- release_builder_template.xml
|-- log
|-- plugins
|-- serve.py
|-- svn_checkout
|-- utils
|   `-- template_builder.py
`-- work

Installers and managers are similar, but we'll start here.  The README.txt is a copy of docs/builder.txt from the releasemanager package, as a starting point.

The archive directory is simply the default place where the builder will place where the builder will construct the archives that it sends back to the manager.

The builder directory itself is of more interest.  The template.py file provides, as an example, the correct way to subclass the base BuildBehavior, and what you own methods must provide, and how they must be constructed in order to be used correctly by the builder.

The configuration file in conf/builder named release_builder_template.xml corresponds to the builder/template.py file, establishing defaults and necessary functional parameters.  The naming of the conf/builder/release_builder_*.xml files should correspond to the projects you intend to advertise, one release_builder file per project, inasmuch as each project should have its own unique build behavior.

The build_host_template.xml file is describes the mandatory configuration elements for a build host.  Though you can define any other arbitrary set of nodes, and will have them available via Amara registered in self._config in the build host, the ones described in the template file must be present for the build host to start and function correctly.

The log directory is simply the default logging path for all builder actions.

The plugins directory will be described in more detail later, but it is designed to hold things like authentication plugins, etc.

The serve.py file is the instantiation script to launch the server.

The svn_checkout and work directories are simply default configurable areas wherein the builder can be asked to do its work.  Paths can be relative to the installation, or absolute.

The utils directory provides a single file, called template_builder.py.  This file simply hooks into the builder core without the service component, creating the archive file that it would normally send to the manager on completion.  In this case it just builds the archive and leaves it in place for extraction, in the event that an administrator would need or want to explicitly build a resource locally, without making use of the whole ReleaseManager heirarchy.  It also presents an excellent starting point for testing new build procedures without having to hook up the entire infrastructure first.

Manager Installation Layout
---------------------------
.
|-- README.txt
|-- conf
|   |-- manager
|   |   `-- release_manager_template.xml
|   `-- project
|       `-- project_definition_template.xml
|-- log
|-- plugins
|-- serve.py
`-- work

As above, the README.txt file is simply a copy of the docs/manager.txt file from the releasemanager package, as a starting point for developers.

The log, plugins, and work directories are all as above, simply a default location in which these operations will or may take place.

The conf directory holds two elements, a place for manager configs, and a place for project configs.  As with all configuration files in the ReleaseManager system, the naming convention is relevant.  Projects will be looked up with "project_definition_", and release manager configs will be looked up with "release_manager_", so that when changing contexts, you can simply say "template" or "my_new_project".  The release manager config describes the mandatory elements for a release manager to start and run correctly with the serve.py script.  The project files must contain a project and its named targets, according to the layout described in the template file.

The serve.py script is, as in the builder, simply the script used to start the builder.  It will register itself with any release manager it has been configured to be aware of, but will not fail to start should any of these be unavailable, though it will throw a warning.  All ReleaseManager serve.py files contain at the top a global variable named "DEFAULT_NAME", which will be used when the serve.py file is called, to find the default release manager config to use.  This may be overridden simply by passing the "-n" flag to the script, and giving it an alternate name.  It is possible to pass in a "-p" flag as well to indicate a new configuration path, but this is not recommended unless you have a specific reason for doing so.  Any configuration element depending on a relative path will be affected by this change.

Installer Installation Layout
-----------------------------
.
|-- README.txt
|-- conf
|   |-- installer
|   |   `-- release_installer_template.xml
|   `-- target
|       |-- dev
|       |-- prod
|       |-- qa
|       `-- test
|           |-- install_behavior_template.xml
|           `-- named_target_template.xml
|-- install_base
|-- log
|-- plugins
|-- serve.py
`-- work

As the others, the README.txt is a simple starting point from docs/installer.txt in the releasemanager package.  The log, plugins, and work directories all provide the same functionality as above.

The conf directory contains both installer and target directories.  The installer directory configures the actual installer service, describing all of the necessary elements for the installer to start and run.  It also contains a list of named targets and environments that the installer intends to advertise to the manager.  The target directory contains, by default, a dev, prod, qa, and test set of directories, corresponding to dev, prod, qa, and test environments.  You can add to or remove from these as necessary, making sure only that the environments referenced by the installer config actually have corresponding directories in target, and that they contain configs for the referenced named targets.

The target directory bears a bit of analysis.  Each environment must contain a config for every named target it intends to support.  If an installer should be able to install both the static web files and the .war archive for a J2EE webapp, it would be something like "named_target_myapp_webapp.xml" and "named_target_myapp_static.xml" with associated install behaviors that appropriately handle the action to be taken.  More detail on how to write and use install behaviors is covered elsewhere, but in its most straightforward form, one simply writes a behavior class that can be __call__'d that understands how to process the installation of a resource.

The install_base directory is simply the default installation path when the installer is built.  This will almost certainly need to be changed in the config for any real project.  However, it serves as a model, that should the "template" install behavior be called, it will unzip the resource it receives into the install_base/template.

Configuration Files
===================

The ReleaseManager system uses a standard convention for its configuration files.  At its simplest, all configuration files start with the pattern:

<item_type
  name="some_name"
  klass="KlassToBuild"
  package="dotted.package.name"
  >
<!-- specific elements here -->
</item_type>

The "name, klass, package" convention is to interact with the builtin KlassBuilder and ConfigLoader system.  This is being used in both this project, and other projects by the author (www.simpleauth.com, www.simplewatcher.com) and, though it has the downside of requiring Amara, presents a very flexible way to build configuration files, allowing classes to build other classes as composed behaviors without having to explicitly import anything other than the KlassBuilder itself.

The configuration files specific to installers, builders, and managers (the services, not the behaviors associated) have in common the following parameters:
  logging_path
  logging_level
  listen_port

The logging elements are simply used in initializing python's standard-library logging module, and unless you need something else, the defaults should be fine.  The listen_port element may need to be tweaked or modified if another service is already listening on the configured port.  The only note is that if you change the manager's listen port, you need to update the affected installers and builders configuration files or they will fail to register with the manager.


Persistence
===========

Persistence in ReleaseManager refers specifically to the maintenance of three specific elements: Registrations, Transactions, and History.  Registrations are the installer and builder instances that register themselves with any release manager.  The location is logged, and a pickled version of its data is stored to be reloaded back whenever a ReleaseManager restarts.  Transactions are specific instances of a request for action logged through a Manager instance.  History is a series of actions recorded by the release manager in regard to any particular transaction.

Builders and Installers are not involved in the persistence machinery in any way.  This is by design, as it would have been an extra dependency, requiring that any installer or builder instance would have to have a python DBAPI available for the particular database used for persistency, as well as having sqlalchemy installed, etc.  Because we want to keep installers and builders as light as possible in their dependencies, this element was left off.

Building Persistence plugins is not difficult.  It will require the use of sqlalchemy, but an example, and the default, is already available in releasemanager.persist.mysql_tables, the method make_tables.  If you need or want to provide greater functionality, or simply want to connect to another type of database, it should be as simple as providing a configuration file named "plugin_persist_{some_name}.xml", and using the "name,package,klass" designators, point it to a package that provides a class that has a "make_tables" method with the same call signature as the example.

Authentication and Authorization
================================

By default, ReleaseManager uses anonymous access for authentication and authorization.  This is not recommended.  Allowing anonymous actions to be taken on arbitrary builders and installers could easily wreak havoc with an environment.  However, because it is not possible to be certain what kind of auth system a client will want to make use of, be it Twisted's Cred system to hook into other systems (for which a plugin is hopefully forthcoming), SimpleAuth (www.simpleauth.com), or any locally devised system.

Because the author is also the maintainer of SimpleAuth and makes extensive use of it elsewhere, it is possible to make use of SimpleAuth as an authentication plugin out of the box.  When generating an installer, builder, or manager, simply pass a "-a simpleauth" at the end of the relman_ctl command, and it will install an auth plugin for use with simpleauth.  It can then be enabled in the config files to make use of the system immediately.  SimpleAuth however is distinct download and install, and though a setuptools driven version is in the works, it is currently a whole-application framework that must be installed and managed on its own.

If you intend to provide an authentication plugin of your own, there is no problem with doing this.  Simply build a package in plugins/auth that provides the authorize and authenticate methods.  As they accept a credentials dictionary, it is possible to create arbitrarily complex authorization and authentication mechanisms, so long as they provide authorize and authenticate.  To enable them, simply name the configuration file in the conf/plugins/auth directory "plugin_auth_[plugin_name].xml", and using the KlassBuilder "name, package, klass" setup, point it to your authentication plugin.  If in doubt, look at the simpleauth version as an example.


Conclusion
==========

While there is certainly a great deal more to be covered, they will be addressed in documentation more explicitly related to the given topics.  Hopefully this overview has been thorough enough to give a clear picture of how the system should be put together.