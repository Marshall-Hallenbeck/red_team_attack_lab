import os
import sys
import argparse
from modules import logger
from pathlib import Path
from modules.CustomConfigParser import CustomConfigParser
from modules.VagrantController import VagrantController

VERSION = 1

if __name__ == "__main__":
    # grab arguments
    parser = argparse.ArgumentParser(description="starts a attack range ready to collect attack data into splunk")
    parser.add_argument("-a", "--action", required=False,
                        choices=['build', 'create_config', 'destroy', 'simulate', 'stop', 'resume', 'dump'],
                        help="action to take on the range, defaults to \"build\", build/destroy/simulate/stop/resume "
                             "allowed")
    parser.add_argument("-t", "--target", required=False,
                        help="target for attack simulation. For mode vagrant use name of the vbox")
    parser.add_argument("-st", "--simulation_technique", required=False, type=str, default="",
                        help="comma delimited list of MITRE ATT&CK technique ID to simulate in the attack_range, "
                             "example: T1117, T1118, requires --simulation flag")
    parser.add_argument("-sa", "--simulation_atomics", required=False, type=str, default="",
                        help="specify dedicated Atomic Red Team atomics to simulate in the attack_range, example: "
                             "Regsvr32 remote COM scriptlet execution for T1117")
    parser.add_argument("-c", "--config", required=False, default="attack_lab.conf",
                        help="path to the configuration file of the attack range")
    parser.add_argument("-lm", "--list_machines", required=False, default=False, action="store_true",
                        help="prints out all available machines")
    parser.add_argument("-dn", "--dump_name", required=False, help="define the dump name")
    parser.add_argument("-v", "--version", default=False, action="store_true", required=False,
                        help="shows current attack_range version")

    # parse them
    args = parser.parse_args()
    ARG_VERSION = args.version
    action = args.action
    target = args.target
    config = args.config
    simulation_techniques = args.simulation_technique
    simulation_atomics = args.simulation_atomics
    list_machines = args.list_machines
    dump_name = args.dump_name

    print("""
    Starting Red Team Attack Lab...
    Created by @Marshall-Hallenbeck
    Original: Splunk Attack Range
    """)

    # parse config
    attack_range_config = Path(config)
    if attack_range_config.is_file():
        print("attack_range is using config at path {0}".format(attack_range_config))
        config_path = str(attack_range_config)
    else:
        print("ERROR: attack_range failed to find a config file at {0}..exiting".format(attack_range_config))
        sys.exit(1)

    # Parse config
    parser = CustomConfigParser()
    config = parser.load_conf(config_path)

    log = logger.setup_logging(config['log_path'], config['log_level'])
    log.info("INIT - attack_range v" + str(VERSION))

    if ARG_VERSION:
        log.info("version: {0}".format(VERSION))
        sys.exit(0)

    if not action and not list_machines:
        log.error('ERROR: Use -a to perform an action or -lm to list available machines')
        sys.exit(1)

    if action == 'simulate' and not target:
        log.error('ERROR: Specify target for attack simulation')
        sys.exit(1)

    if action == 'dump' and not dump_name:
        log.error('ERROR: Specify --dump_name for dump command')
        sys.exit(1)

    # lets give CLI priority over config file for pre-configured techniques
    if simulation_techniques:
        pass
    else:
        simulation_techniques = config['art_run_techniques']

    if not simulation_atomics:
        simulation_atomics = 'no'

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

    if action == 'simulate':
        controller.simulate(target, simulation_techniques, simulation_atomics)

    if action == 'dump':
        controller.dump(dump_name)
