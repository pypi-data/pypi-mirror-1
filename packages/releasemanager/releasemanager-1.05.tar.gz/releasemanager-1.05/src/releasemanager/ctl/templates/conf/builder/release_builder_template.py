_config_ = dict(
    name="template",
    klass="TemplateBuildBehavior",
    package="builder.template",
    svn_user = '',
    svn_pass = '',
    svn_url = 'http://releasemanager.googlecode.com/svn/',
    svn_target = 'releasemanager',
    svn_work_dir = 'svn_checkout',
    ignore_clean_error = True,
    archive_output = 'archive',
    output_targets = dict(
        file = [
            dict(target='template', name='releasemanager.zip'),
        ],
    ),
    logging_path = 'log',
    logging_level = 'DEBUG',
    auth_role = 'relman_template_build',
)