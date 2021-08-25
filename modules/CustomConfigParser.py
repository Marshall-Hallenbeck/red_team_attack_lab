# ORIGINAL: https://github.com/splunk/attack_range_local/
import configparser
import sys


class CustomConfigParser:
    def __init__(self):
        self.settings = {}

    def load_conf(self, config_path):
        """Provided a config file path and a collections of type dict,
        will return that collections with all the settings in it"""

        config = configparser.RawConfigParser()
        config.read(config_path)
        for section in config.sections():
            for key in config[section]:
                try:
                    self.settings[key] = config.get(section, key)
                except Exception as e:
                    print("ERROR - with configuration file at {0} failed with error {1}".format(config_path, e))
                    sys.exit(1)

        return self.settings
