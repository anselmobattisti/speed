#!/bin/bash

BASEDIR=$(dirname $0)

for file in "$BASEDIR"/files/*; do

  if [ "${file: -4}" == ".yml" ]; then
    filename=$(basename -- "$file")
    filename="${filename%.*}"
    log_path="$BASEDIR/logs/${filename}/"
    if [ ! -d "$log_path" ]; then
      mkdir "$log_path"
    fi

    export BIGGEST_SEGMENT="False"
    export ALGORITHM="speed"
    python3 ../../main.py --logs "$log_path/speed" --config ./config/config_simulation.yml --zones ./config/zone_topology.yml --entities "$file" &

    export BIGGEST_SEGMENT="True"
    export ALGORITHM="random"
    python3 ../../main.py --logs "$log_path/random" --config ./config/config_simulation.yml --zones ./config/zone_topology.yml --entities "$file" &

    export BIGGEST_SEGMENT="True"
    export ALGORITHM="greedy"
    python3 ../../main.py --logs "$log_path/greedy" --config ./config/config_simulation.yml --zones ./config/zone_topology.yml --entities "$file" &

  fi

done;

