_config_ = dict(
    name="template",
    klass="ReleaseInstaller",
    package="releasemanager.installer.releasedaemon",
    logging_path = 'log',
    logging_level = 'DEBUG',
    named_targets = dict( 
        target = [
            dict(name='named_target_template', environment='test'),
        ],
    ),
    listen_port = 9997,
    release_managers = dict(
        host = [
            dict(name='localhost', port=10000),
        ],
    ),
    # Uncomment these lines to enable simpleauth
    # auth_plugin = 'simpleauth',
    # svc_role = 'relman_svc',
)
