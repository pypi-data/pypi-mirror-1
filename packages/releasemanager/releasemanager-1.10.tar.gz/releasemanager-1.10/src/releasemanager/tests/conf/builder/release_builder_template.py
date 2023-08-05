import os
from releasemanager.tests import TEST_CONF_PATH

_config_ = dict(
    name="template",
    klass="TemplateBuildBehavior",
    package="releasemanager.tests.modules.builder.template",
    svn_user = '',
    svn_pass = '',
    svn_url = 'http://releasemanager.googlecode.com/svn/',
    svn_target = 'releasemanager',
    svn_work_dir = os.path.join(TEST_CONF_PATH, "..%ssvn_checkout" % (os.sep)),
    ignore_clean_error = True,
    archive_output = os.path.join(TEST_CONF_PATH, "..%sarchive" % (os.sep)),
    output_targets = dict(
        file = [
            dict(target='template', name='releasemanager.zip'),
        ],
    ),
    logging_path = os.path.join(TEST_CONF_PATH, "..%slog" % (os.sep)),
    logging_level = 'DEBUG',
    auth_role = 'relman_template_build',
)