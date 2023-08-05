import os, sys
import shutil

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

class BaseAppCreator(object):
    """base application creator"""
    def __init__(self, base_path, name):
        self.build_path = os.path.join(base_path, name)
        self.conf_path = os.path.join(self.build_path, "conf")
        self.log_path = os.path.join(self.build_path, "log")
        self.work_path = os.path.join(self.build_path, "work")
        self.app_name = name
    
    def base_build(self):
        if not os.path.isdir(self.build_path):
            os.mkdir(self.build_path)
        if not os.path.isdir(self.conf_path):
            os.mkdir(self.conf_path)        
        if not os.path.isdir(self.log_path):
            os.mkdir(self.log_path)
        if not os.path.isdir(self.work_path):
            os.mkdir(self.work_path)
    
    def generate(self, name):
        raise NotImplementedError("Must implement build layout in subclass")
    

class ManagerCreator(BaseAppCreator):
    """a manager creator"""
    def generate(self):
        self.base_build()
        project_template_dir = "%s/conf/project" % TEMPLATE_DIR
        manager_template_dir = "%s/conf/manager" % TEMPLATE_DIR
        project_install_dir = "%s/project" % self.conf_path
        manager_install_dir = "%s/manager" % self.conf_path
        if not os.path.isdir(project_install_dir):
            os.mkdir(project_install_dir)
        if not os.path.isdir(manager_install_dir):
            os.mkdir(manager_install_dir)
        manager_template = "release_manager_template.py"
        project_template = "project_definition_template.py"
        shutil.copy("%s/%s" % (project_template_dir, project_template), "%s/%s" % (project_install_dir, project_template))
        shutil.copy("%s/%s" % (manager_template_dir, manager_template), "%s/%s" % (manager_install_dir, manager_template))
        srv_file = "%s/manager_serve.py" % TEMPLATE_DIR
        shutil.copy(srv_file, "%s/serve.py" % self.build_path)
        readme = "%s/MANAGER.txt" % TEMPLATE_DIR
        shutil.copy(readme, "%s/README.txt" % self.build_path)
        
        

class InstallerCreator(BaseAppCreator):
    """an installer creator"""

    def generate(self):
        self.base_build()
        target_conf = "%s/conf/target" % TEMPLATE_DIR
        target_base = "%s/target" % self.conf_path
        if not os.path.isdir(target_base):
            os.mkdir(target_base)
        target_dirs = [
            "%s/target/prod" % self.conf_path,
            "%s/target/dev" % self.conf_path,
            "%s/target/qa" % self.conf_path,
            "%s/target/test" % self.conf_path,
        ]
        for d in target_dirs:
            if not os.path.isdir(d):
                os.mkdir(d)
        target_templates = [
            "named_target_template.py",
            "install_behavior_template.py",
        ]
        for f in target_templates:
            shutil.copy("%s/test/%s" % (target_conf, f), "%s/test/%s" % (target_base, f))
        installer_conf = "%s/conf/installer" % TEMPLATE_DIR
        installer_template = "release_installer_template.py"
        installer_dir = "%s/installer" % self.conf_path
        if not os.path.isdir(installer_dir):
            os.mkdir(installer_dir)
        install_base = "%s/install_base" % self.build_path
        if not os.path.isdir(install_base):
            os.mkdir(install_base)
        shutil.copy("%s/%s" % (installer_conf, installer_template), "%s/%s" % (installer_dir, installer_template))
        srv_file = "%s/installer_serve.py" % TEMPLATE_DIR
        shutil.copy(srv_file, "%s/serve.py" % self.build_path)
        readme = "%s/INSTALLER.txt" % TEMPLATE_DIR
        shutil.copy(readme, "%s/README.txt" % self.build_path)
        

class BuilderCreator(BaseAppCreator):
    """a builder creator"""
    def generate(self):
        self.base_build()
        builder_template_dir = "%s/conf/builder" % TEMPLATE_DIR
        builder_behavior_dir = "%s/builder" % TEMPLATE_DIR
        builder_install_dir = "%s/builder" % self.conf_path
        behavior_install_dir = "%s/builder" % self.build_path
        utils_install_dir = "%s/utils" % self.build_path
        svn_checkout_dir = "%s/svn_checkout" % self.build_path
        archive_dir = "%s/archive" % self.build_path
        for d in [builder_install_dir, behavior_install_dir, svn_checkout_dir, archive_dir, utils_install_dir]:
            if not os.path.isdir(d):
                os.mkdir(d)
        template_files = [
            "build_host_template.py",
            "release_builder_template.py",
        ]
        for f in template_files:
            shutil.copy("%s/%s" % (builder_template_dir, f), "%s/%s" % (builder_install_dir, f))
        builder_files = [
            "template.py",
            "__init__.py",
        ]
        for f in builder_files:
            shutil.copy("%s/%s" % (builder_behavior_dir, f), "%s/%s" % (behavior_install_dir, f))
        srv_file = "%s/builder_serve.py" % TEMPLATE_DIR
        readme = "%s/BUILDER.txt" % TEMPLATE_DIR
        build_util = "%s/utils/template_builder.py" % builder_behavior_dir
        files_and_targets = [
            (srv_file, "%s/serve.py" % self.build_path),
            (readme, "%s/README.txt" % self.build_path),
            (build_util, "%s/template_builder.py" % utils_install_dir),
        ]
        for f, t in files_and_targets:
            shutil.copy(f, t)
        


class PluginCreator(object):
    plugins = {
        "auth" : {
            "simpleauth" : ["simpleauth.py", "plugin_auth_simpleauth.py"],
        }
    }

    def __init__(self, plugin_type, plugin_name, install_base=None):
        plugin_base = "%s/plugins" % TEMPLATE_DIR
        self.conf_base = "%s/plugins/conf" % TEMPLATE_DIR
        self.conf_type = "%s/%s" % (self.conf_base, plugin_type)
        self.plugin_name = plugin_name
        self.plugin_base = "%s/%s" % (plugin_base, plugin_type)
        self.plugin_type = plugin_type
        self.install_base = install_base
        self.local_conf_base = "%s/conf/plugins" % self.install_base
        self.local_conf_full = "%s/%s" % (self.local_conf_base, plugin_type)
        self.plugin_file = None
        if plugin_type in self.plugins:
            if plugin_name in self.plugins[plugin_type]:
                self.plugin_file = os.path.join(self.plugin_base, self.plugins[plugin_type][plugin_name][0])
                self.plugin_conf = os.path.join(self.conf_type, self.plugins[plugin_type][plugin_name][1])
                if not os.path.isfile(self.plugin_file):
                    self.plugin_file = None
                if not os.path.isfile(self.plugin_conf):
                    self.plugin_conf = None
    
    def build_base(self):
        blank = ""
        self.plugin_path = os.path.join(self.install_base, "plugins")
        self.plugin_type_path = os.path.join(self.install_base, "plugins%s%s" % (os.sep, self.plugin_type))
        for d in [self.plugin_path, self.plugin_type_path]:
            if not os.path.isdir(d):
                os.mkdir(d)
            if not os.path.isfile(os.path.join(d, "__init__.py")):
                open(os.path.join(d, "__init__.py"), 'w').write(blank)
                    
        for d in [self.local_conf_base, self.local_conf_full]:
            if not os.path.isdir(d):
                os.mkdir(d)


    def install(self):
        self.build_base()
        install_to = "%s/plugins/%s" % (self.install_base, self.plugin_type)
        if self.plugin_file:
            shutil.copy(self.plugin_file, install_to)
        else:
            raise UserWarning("Could not install plugin %s to %s!" % (self.plugin_name, install_to))
        
        if self.plugin_conf:
            shutil.copy(self.plugin_conf, self.local_conf_full)
        else:
            raise UserWarning("Could not install configuration for plugin %s to %s!" % (self.plugin_name, self.local_conf_full))