import os
from releasemanager.tests import TEST_CONF_PATH

_config_ = dict(
    name="template",
    klass="BuildHost",
    package="releasemanager.builder.buildhost",
    projects = dict(
        project = [
            dict(name="template"),
        ],
    ),
    work_dir = os.path.join(TEST_CONF_PATH, "..%swork" % (os.sep)),
    build_file = 'resource.zip',
    logging_path = os.path.join(TEST_CONF_PATH, "..%slog" % (os.sep)), 
    logging_level = 'DEBUG',
    listen_port = 9999,
    release_managers = dict(
        host = [
            dict(name="localhost", port="10000"),
        ],
    ),
    tester_value = False,
    # Uncomment these lines to enable simpleauth
    # auth_plugin = 'simpleauth',
    # svc_role = 'relman_svc',
)
