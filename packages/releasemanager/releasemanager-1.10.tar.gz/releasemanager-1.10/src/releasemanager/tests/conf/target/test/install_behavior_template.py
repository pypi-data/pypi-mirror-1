import os
from releasemanager.tests import TEST_CONF_PATH

_config_ = dict(
    name="template",
    klass="TemplateInstallBehavior",
    package="releasemanager.installer._installbehavior",
    install_path = os.path.join(TEST_CONF_PATH, "..%sinstall_base" % (os.sep)),
    install_target = 'template',
    destroy_target = 'true',
    work_dir = os.path.join(TEST_CONF_PATH, "..%swork" % (os.sep)),
    ignore_clean_error = 'false',
    auth_role = 'relman_template_install',
)