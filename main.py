import simpy
import argparse

from SimPlacement.helper import Helper
from SimPlacement.setup import Setup

from SPEED.helpers.zone import ZoneHelper
from SPEED.simulation import SPEEDSimulation


def main():

    parser = argparse.ArgumentParser(prog='SimPlacement')
    parser.add_argument('--logs', default="./examples/basic/logs", help='Path where the log files will be saved.')
    parser.add_argument('--config', default="./examples/basic/config.yml", help='Simulation config file.')
    parser.add_argument('--entities', default="./examples/basic/entities.yml", help='Entities config file.')
    parser.add_argument('--zones', default="./examples/basic/zones.yml", help='Entities zone config file.')
    parser.add_argument('--packets',  help='Simulation packets file.')

    args = parser.parse_args()

    print("Loading configuration file...")
    config = Helper.load_yml_file(args.config)

    print("Loading entities...")
    environment = Setup.load_entities(args.entities)

    environment['zones'] = ZoneHelper.load(
        data_file=args.zones,
        environment=environment
    )

    se = SPEEDSimulation(
        env=simpy.Environment(),
        config=config["simulation"],
        environment=environment
    )

    # change the path where the simulation will save the logs.
    se.log.set_log_path(args.logs)
    print("Running simulation...")
    se.run()


if __name__ == "__main__":
    main()
