# ORIGINAL: https://github.com/splunk/attack_range_local/
import sys
import argparse
from modules import logger
from pathlib import Path
from modules.CustomConfigParser import CustomConfigParser
from modules.VagrantController import VagrantController
import os

VERSION = 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starts Red Team Attack Lab")
    parser.add_argument(
        "-a", "--action",
        required=False,
        choices=['build', 'create_config', 'destroy', 'stop', 'resume', 'status'],
        default='create_config',
        help="action to take in the lab: build/create_config/destroy/stop/resume/status allowed \ndefault: create_config"
    )
    parser.add_argument(
        "-c", "--config",
        required=False,
        default="attack_lab.conf",
        help="path to the configuration file of the attack range"
    )
    parser.add_argument(
        "-v", "--version",
        default=False,
        action="store_true",
        required=False,
        help="shows current attack_lab version"
    )

    args = parser.parse_args()
    ARG_VERSION = args.version
    action = args.action
    config_file = args.config

    print("""
    Starting Red Team Attack Lab...
    Created by @Marshall-Hallenbeck
    Original: Splunk Attack Range
    """)

    attack_lab_config = Path(os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file))
    if attack_lab_config.is_file():
        print("attack_lab is using config at path {0}\n".format(attack_lab_config))
        config_path = str(attack_lab_config)
    else:
        print("ERROR: attack_lab failed to find a config file at {0}..exiting".format(attack_lab_config))
        sys.exit(1)

    parser = CustomConfigParser()
    config = parser.load_conf(attack_lab_config)
    log_location = config['log_path']
    log_level = config['log_level']

    log = logger.setup_logging(log_location, log_level)

    if ARG_VERSION:
        log.info("version: {0}".format(VERSION))
        sys.exit(0)

    controller = VagrantController(config, log)

    if action == 'create_config':
        pass

    if action == 'build':
        controller.build()

    if action == 'destroy':
        controller.destroy()

    if action == 'stop':
        controller.stop()

    if action == 'resume':
        controller.resume()

    if action == 'status':
        controller.list_machines()
