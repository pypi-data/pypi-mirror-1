import os
from releasemanager.tests import TEST_CONF_PATH

_config_ = dict(
    name="template",
    klass="NamedTarget",
    package="releasemanager.installer.target",
    install_behavior = 'install_behavior_template',
    logging_path = os.path.join(TEST_CONF_PATH, "..%slog" % (os.sep)), 
    logging_level = 'DEBUG',
)