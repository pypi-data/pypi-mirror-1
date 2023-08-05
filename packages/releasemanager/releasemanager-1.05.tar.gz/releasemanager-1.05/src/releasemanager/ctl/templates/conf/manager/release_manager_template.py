_config_ = dict(
    name="template",
    klass="ReleaseManager",
    package="releasemanager.manager",
    registration = [
        dict(name='release_installer', action='install', 
            param = [
               dict(name='host', required="true",),
               dict(name='port', required="true",),
            ],
        ),
        dict(name='build_host', action='build', 
            param = [
               dict(name='host', required="true",),
               dict(name='port', required="true",),
            ],
        ),
    ],
    logging_path = 'log',
    logging_level = 'DEBUG',
    listen_port = 10000,
    projects = dict(all='false', dir='',
        project = [
            dict(name='template'),
            dict(name='oasis_webapp'),
            dict(name='oasis_apache'),
            dict(name='oasis_dropper'),
        ],
    ),
    work_dir = 'work',
    db_type = 'mysql',
    db_uri = 'mysql://user:password@localhost:3306/releasemanager',
    # uncomment these lines to enable simpleauth
    # auth_plugin = 'simpleauth',
    # svc_role = 'relman_svc',
)
