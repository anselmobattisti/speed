#!/bin/bash

BASEDIR=/home/battisti/versionado/speed/experiments/A2

n=0
maxjobs=3

for file in "$BASEDIR"/files/*; do

  # remove the topology files
  if [ "${file: -8}" == "topo.yml" ]; then
    continue
  fi

  if [ "${file: -4}" == ".yml" ]; then
    filename=$(basename -- "$file")
    filename="${filename%.*}"
    log_path="$BASEDIR/logs/${filename}/"
    if [ ! -d "$log_path" ]; then
      mkdir "$log_path"
    fi

    topology_name="${file%.*}_topo.yml"

    export BIGGEST_SEGMENT="False"
    export ALGORITHM="speed"

#    python3 -m scalene --html --reduced-profile --outfile=out.html ../../main.py --logs "$log_path/speed" --config ./config/config_simulation.yml --zones "$topology_name" --entities "$file"

#    export ALGORITHM="random"
#    python3 ../../main.py --logs "$log_path/random" --config ./config/config_simulation.yml --zones "$topology_name" --entities "$file" &

#     python3 ../../main.py --logs "$log_path/speed" --config ./config/config_simulation.yml --zones "$topology_name" --entities "$file" &

     python3 /home/battisti/versionado/SimPlacement/main.py --logs "$log_path/domain" --config ./config/config_simulation.yml --entities "$file" --sfc_auction_sim --not_auction &

#     python3 /home/battisti/versionado/SimPlacement/main.py --logs "$log_path/auction" --config ./config/config_simulation.yml --entities "$file" --sfc_auction_sim &

#    export ALGORITHM="greedy"
#    python3 ../../main.py --logs "$log_path/greedy" --config ./config/config_simulation.yml --zones "$topology_name" --entities "$file" &

  fi

  # limit jobs
  if (( $(($((++n)) % $maxjobs)) == 0 )) ; then
      wait # wait until all have finished (not optimal, but most times good enough)
      echo $n wait
  fi
done;

#python3 ../../main.py --logs "$log_path/speed" --config ./config/config_simulation.yml --zones "$topology_name" --entities "$file" &

#     python3 -m scalene --html --reduced-profile --outfile=out.html ../../main.py --logs "$log_path/speed" --config ./config/config_simulation.yml --zones "$topology_name" --entities "$file"