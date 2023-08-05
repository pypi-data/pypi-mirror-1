_config_ = dict(
    name="template",
    klass="BuildHost",
    package="releasemanager.builder.buildhost",
    projects = dict(
        project = [
            dict(name="template"),
        ],
    ),
    work_dir = 'work',
    build_file = 'resource.zip',
    logging_path = 'log', 
    logging_level = 'DEBUG',
    listen_port = 9999,
    release_managers = dict(
        host = [
            dict(name="localhost", port="10000"),
        ],
    ),
    # Uncomment these lines to enable simpleauth
    # auth_plugin = 'simpleauth',
    # svc_role = 'relman_svc',
)
