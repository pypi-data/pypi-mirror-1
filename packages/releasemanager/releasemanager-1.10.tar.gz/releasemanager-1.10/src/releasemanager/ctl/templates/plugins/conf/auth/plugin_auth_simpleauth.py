_config_ = dict(
    name="simpleauth",
    klass="SimpleAuthPlugin",
    package="plugins.auth.simpleauth",
    db=dict(
        type='mysql',
        uri='mysql://username:password@localhost:3306/simple_auth',
    ),
    svc_name="releasemanager",
)