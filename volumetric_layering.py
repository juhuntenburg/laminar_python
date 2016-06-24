# prior to this:
# 1.create a jar file with all the classes:
# jar cvf intensity.jar de/mpg/cbs/python/IntensityBackgroundEstimator.class de/mpg/cbs/utilities/Numerics.class de/mpg/cbs/libraries/ImageStatistics.class
# 2.compile with jcc:
# python -m jcc --jar intensity.jar --python intensity --build --classpath /home/pilou/Code/cbs/bazin --install --install-dir /home/pilou/Code/cbs/bazin/pylibs/
# 3.export library path to python:
# export PYTHONPATH=$PYTHONPATH:/home/pilou/Code/cbs/bazin/pylibs

import argparse
import numpy as np
import nibabel as nb
import cbstools
import os
from io_volume import load_volume, save_volume

def layering(gwb_levelset, cgb_levelset, lut_dir, number_layers=10,
             save_data=True, base_name=None):

    # load the data as well as filenames and headers for saving later
    gwb_data, im_header, im_affine = load_volume(gwb_levelset)
    cgb_data, _, _ = load_volume(cgb_levelset)

    if not base_name:
        dir_name = os.path.dirname(gwb_levelset)
        base_name = os.path.basename(gwb_levelset)
        base_name = base_name[:base_name.find('.')]

    cbstools.initVM(initialheap='6000m', maxheap='6000m')
    lamination=cbstools.LaminarVolumetricLayering()
    lamination.setDimensions(gwb_data.shape[0],gwb_data.shape[1],gwb_data.shape[2])
    zooms = [x.item() for x in im_header.get_zooms()]
    lamination.setResolutions(zooms[0], zooms[1], zooms[2])

    lamination.setInnerDistanceImage(cbstools.JArray('float')((gwb_data.flatten('F')).astype(float)))
    lamination.setOuterDistanceImage(cbstools.JArray('float')((cgb_data.flatten('F')).astype(float)))
    lamination.setNumberOfLayers(number_layers)
    lamination.setTopologyLUTdirectory(lut_dir);
    lamination.execute()

    depth_data=np.reshape(np.array(lamination.getContinuousDepthMeasurement(),dtype=np.float32),gwb_data.shape,'F')
    profile_data=np.reshape(np.array(lamination.getDiscreteSampledLayers(),dtype=np.uint32),gwb_data.shape,'F')

    save_volume(os.path.join(dir_name, base_name+'_depth.nii.gz'),
                depth_data, im_affine, header=im_header)
    save_volume(os.path.join(dir_name, base_name + '_profiles.nii.gz'),
                profile_data, im_affine, header=im_header)

    return profile_data, depth_data
