from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SPEED.helpers.zone import ZoneHelper

import os

# assign directory
directory = 'files'

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)

    if os.path.isfile(f):

        if len(f.split('topo')) == 2:

            fname = "imgs/{}".format(filename.replace(".","_")+".dot")
            fname_img = "imgs/{}".format(filename.replace(".","_")+".png")
            dot_str = ZoneHelper.build_dot_from_zone_file(
                file=f
            )

            print(fname)
            with open(fname, 'w') as file:
                file.write(dot_str)

            cmd = " dot -Tpng {} > {}.png".format(fname, fname_img)
            os.system(cmd)
