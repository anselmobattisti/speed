import simpy
import random

import os
import argparse

from SimPlacement.helper import Helper
from SimPlacement.setup import Setup


def main():

    parser = argparse.ArgumentParser(prog='SimPlacement')
    parser.add_argument('--logs', default="./examples/basic/logs", help='Path where the log files will be saved.')
    parser.add_argument('--config', default="./examples/basic/config.yml", help='Simulation config file.')
    parser.add_argument('--entities', default="./examples/basic/entities.yml", help='Entities config file.')
    parser.add_argument('--packets',  help='Simulation packets file.')

    args = parser.parse_args()

    print("Loading configuration file...")
    config = Helper.load_yml_file(args.config)

    print("Loading entities...")
    environment = Setup.load_entities(args.entities, args.packets, args.flows)

    env = simpy.Environment()

    seed = config["simulation"]['seed']
    random.seed(seed)

    se = AuctionSimulation(
        env=env,
        config=config["simulation"],
        environment=environment,
        reputation=reputation,
        allow_other_domains=args.allow_other_domains
    )

    # change the path where the simulation will save the logs.
    se.log.set_log_path(args.logs)
    print("Running simulation...")
    se.run()


if __name__ == "__main__":
    main()
