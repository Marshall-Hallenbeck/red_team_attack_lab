# ORIGINAL: https://github.com/splunk/attack_range_local/
import sys
import argparse
from modules import logger
from pathlib import Path
from modules.CustomConfigParser import CustomConfigParser
from modules.VagrantController import VagrantController

VERSION = 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starts Red Team Attack Lab")
    parser.add_argument(
        "-a", "--action",
        required=False,
        choices=['build', 'create_config', 'destroy', 'stop', 'resume'],
        help="action to take in the lab, defaults to \"build\", build/destroy/stop/resume allowed"
    )
    parser.add_argument(
        "-c", "--config",
        required=False,
        default="attack_lab.conf",
        help="path to the configuration file of the attack range"
    )
    parser.add_argument(
        "-lm", "--list_machines",
        required=False,
        default=False,
        action="store_true",
        help="prints out all available machines"
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
    config = args.config
    list_machines = args.list_machines

    print("""
    Starting Red Team Attack Lab...
    Created by @Marshall-Hallenbeck
    Original: Splunk Attack Range
    """)

    # parse config
    attack_lab_config = Path(config)
    if attack_lab_config.is_file():
        print("attack_lab is using config at path {0}".format(attack_lab_config))
        config_path = str(attack_lab_config)
    else:
        print("ERROR: attack_lab failed to find a config file at {0}..exiting".format(attack_lab_config))
        sys.exit(1)

    # Parse config
    parser = CustomConfigParser()
    config = parser.load_conf(config_path)

    log = logger.setup_logging(config['log_path'], config['log_level'])
    log.info("INIT - attack_lab v" + str(VERSION))

    if ARG_VERSION:
        log.info("version: {0}".format(VERSION))
        sys.exit(0)

    if not action and not list_machines:
        log.error('ERROR: Use -a to perform an action or -lm to list available machines')
        sys.exit(1)

    controller = VagrantController(config, log)

    if list_machines:
        controller.list_machines()
        sys.exit(0)

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
