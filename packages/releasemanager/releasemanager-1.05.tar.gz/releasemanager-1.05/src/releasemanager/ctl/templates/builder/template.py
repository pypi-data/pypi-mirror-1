#!/usr/bin/env python
import os, sys
import shutil, logging

from releasemanager import utils
from releasemanager.builder.base import BuildBehavior


class TemplateBuildBehavior(BuildBehavior):
    """a template build behavior"""
    

    def _create_component_markers(self):
        self.component_markers = {
            'all' : [self.makeProjectZip],
        }
        

    def makeProjectZip(self, unique):
        """zip the project.  unique is necessary for all build behavior methods, 
           to indicate what directory they should be using for working, 
           archiving, etc, to keep multiple user requests separate
        """
        base_path = self._build_unique_base_path(unique)
        archive_path = self._build_unique_archive_path(unique)
        base_with_target = os.path.join(base_path, str(self._config.svn_target))
        if not os.path.isdir(base_with_target):
            os.mkdir(base_with_target)
        logging.info("Creating Project zip file for %s" % str(self._config.svn_target).capitalize())
        os.chdir(base_with_target)
        filename = "releasemanager.zip"
        utils.makeZip(base_with_target, archive_path, filename, work_dir=base_path)
        utils.clean(base_path, str(self._config.svn_target), self.svn_work_dir, True)

