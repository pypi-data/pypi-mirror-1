import logging, datetime
import os

class ReleaseLogger(object):
    """provides extended logging functionality"""
    def __init__(self, config, configPath=None):
        today = datetime.datetime.now()
        log_dir = str(config.logging_path)
        if not log_dir.startswith("/"):
            log_dir = os.path.join(os.path.join(configPath, "../"), log_dir)
        logging.basicConfig(level=getattr(logging, str(config.logging_level)),
                            format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                            filename='%s%s%s.%s.log' % (str(config.logging_path), os.sep, str(config.klass), today.strftime("%Y%m%d%H%M")),
                            filemode='a')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        self.logger = logging.getLogger('')
    
    def log(self, msg):
        logging.info(msg)