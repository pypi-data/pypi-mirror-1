the purpose of this document is to outline the elements of the application that
need tests, and the feasibility of creating those tests.  while the installer and
builder already have workable doctests, their truth/false conditions are not entirely
satisfactory.  the releasedaemon and buildhost wrappers to the builder/installer 
behaviors are fairly adequately tested though, and i feel confident enough with
their functionality.

what remains then is to go through the source and document the intent of at least
every publicly exposed method, and create a test for it, or at least involve its
functionality in a test explicitly, rather than behind the scenes.  

similarly, the goal and methodology of the persistance and history components was never
too clearly examined, and i don't believe it is working entirely correctly.  also, i 
have begun writing code to create new history records based on messages sent back
by the installer and builder at completion.  this needs to be done more cleanly, and
integrated into each potential failure step.  it might be good, too, to extend the
history to include "from which host" the response messages refer to, for ease of 
troubleshooting and traceback.

finally, while it may not be possible to cleanly or consistently mock up either an
svn repository or an xmlrpc server, it might be worthwhile to create my own test
runner that is smart enough to run the off-line tests as well as the online tests.

also, if a RoR version of releasemanager is to be written, this test documentation
will be the right way to start defining necessary features and functionality beyond
the readme.

Auth
----

the auth module contains no submodules and three classes.  AnonymousAuth, AuthMaker,
and PluginBase.  AuthMaker is the most important, and only necessarily testable,
module within the releasemanager system.  AuthMaker provides the ability to call
authenticate and authorize methods as generically as possible.  This means that if 
a particular installer or builder provides an auth plugin of some kind, the same 
server logic is run regardless.  If no plugin is provided or indicated, then AuthMaker
defaults to using AnonymousAuth which simply returns true for both authenticate and 
authorize.  Insecure and not recommended, but provided as a handy default to get up 
and running.  

test: test that it can be instantiated, and that anonymous auth always returns true.


Builder
-------

the builder module contains two submodules and a single module level class.  The module
level class is ReleaseBuilder, and is, in some senses, the most critical single element
of the whole releasemanager system.  It is ReleaseBuilder that actually checks out
a project, puts it together, and prepares it for processing.

However, ReleaseBuilder itself is simply an aggregation point for other functionality.
ReleaseBuilder is responsible for setting up loggers, configuration directories, and 
constructing its build behavior.  The exposed "build" method from ReleaseBuilder is an
aggregation of behavior from the base.BuildBehavior class, and simply defers to it 
when called.

base.BuildBehavior then is where most of the intelligence for the ReleaseBuilder class
actually takes place.  BuildBehavior takes care of doing all the grunt work of building
a project.  It cleans working directories, establishes temporary workspace, checks
projects out from subversion, and traps around errors, setting logs and responses.

However.  That however deserves a period of its own, so it got one.  However, even 
BuildBehavior doesn't *really* do the actual build.  It wouldn't know how.  Every 
project is assumed to have any number of potential components, and any number of 
necessary actions to perform in order to correctly build.  This can be as simple as
creating a zip file, but as complex as running make, compiling things, running ant 
scripts, building an rpm from a .spec file... any action that is required, and any
series of actions that may be required, to get a set of components for a project into
the proper state for release.

There's no way any one class could be responsible for that kind of complexity.  To 
this end, BuildBehavior implements a single, necessarily overridable method, called 
"_create_component_markers".  This should set a dict of components for BuildBehavior
that describes all the components of a particular project, and what function is 
associated with a given component.  All functions in the {name : [func]}
style dictionary returned by _create_component_markers must take a signature of 
"func(unique)", where unique is a randomly (or non-randomly, should you choose) 
generated marker to differentiate a particular invocation of BuildBehavior.__call__,
since otherwise in a largely distributed system, multiple simultaneous requests could
easily overwrite one another's builds.

The only required tag for the dict returned by _create_component_markers is "all",
which should contain a list of all functions, and the order they should be processed in
to produce a full project.  In fact, this is often the most useful case.  Though there
are worthwhile use cases for splitting the build of a project into components, for
most projects, while they may in fact have multiple components, the only common use 
case will be to build all associated components at once, to say the project has been
built.  An example would be something like a .war file for a java webapp, along with
the static content files for apache, and some utility jar files generated for batch
processing, all produced from the same codebase.

Finally, the buildhost module contains only one class, BuildHost.  This class is
responsible for interacting in a nicely networked and distributed way with the rest
of the releasemanager system.  It is responsible for building lists of available
projects, advertising those projects to the configured releasemanager nodes, handling
authentication/authorization for particular build requests, and creating index files 
in response to named targets for install to be processed by the release manager.

test: ReleaseBuilder.build needs a test.  One handy thing about this test is that,
if it does work correctly, it, of necessity, tests all of the build behavior logic
as well.  Not enough to say that build behavior doesn't need its own tests, but 
simply that it will force an invocation of at least one path through the logic.

BuildBehavior, of course, should have its own tests.  However, for better or worse, 
any logical faults in build behavior will show up simply because ReleaseBuilder.build
will fail its test.  Since all of the internal work of BuildBehavior is related to
setting up configurations and creating working directories, etc, creating tests for 
it is, in some ways, more a matter of testing for the negative, to prove that it 
breaks when it should break, rather than that it works.  And while that's necessary
there are other, bigger win tests still to be written that don't take as long.  This
means that BuildBehavior will have to be come back to.

BuildHost needs tests for build, report, and load/reload.  these tests have been built.

Config
------

Not that it's not a good idea to write tests for everything, but the ConfigLoader, 
PyConfigLoader, XmlConfigLoader, and KlassBuilder classes have been in use for quite
some time on more than a few projects i've worked on.  i'll write tests for them when
the other more critical tests are written.

Ctl
---

the ctl module is there to support the relman_ctl script for creating new projects. 
While important to test to prove it works, it is currently in need of some refactoring
and the tests will wait until that refactoring happens.

Installer
---------

the installer module has three submodules.  releasedaemon, target, and _installbehavior.
releasedaemon contains only the ReleaseInstaller class, which already has tests for 
its install, reload, and report methods.

the target module contains both the NamedTarget class and the InstallBehavior class.
NamedTargets aggregate their install method from an InstallBehavior.  However, much
like the BuildBehavior above for ReleaseBuilder, while the InstallBehavior class 
provides a solid foundation on which to build others, it does not, itself, know
how to actually install any particular resource.  It has a single "_install" method
that must be overridden in any subclass to provide the actuall install methodology.

NamedTarget already has tests for resetVersion, getVersion, and install.

_installbehavior is just a helper module that provides some simple install behavior 
examples.  Provided is "unarchive" for zip files, and "install" for putting a file
directly in place, as is.  It is meant to be used either for cases where an install
needs very little complex action to occur, and to be integrated into tests.