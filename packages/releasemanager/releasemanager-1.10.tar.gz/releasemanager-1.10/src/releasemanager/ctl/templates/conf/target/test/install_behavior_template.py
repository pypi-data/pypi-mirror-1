_config_ = dict(
    name="template",
    klass="TemplateInstallBehavior",
    package="releasemanager.installer._installbehavior",
    install_path = 'install_base',
    install_target = 'template',
    destroy_target = 'false',
    work_dir = 'work',
    ignore_clean_error = 'false',
    auth_role = 'relman_template_install',
)