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
from io_volume import load_volume #, save_volume

def layering(gwb_levelset, cgb_levelset, lut_dir, number_layers=10):

    # load the data as well as filenames and headers for saving later
    gwb_data, im_header, im_affine = load_volume(gwb_levelset)
    cgb_data, _, _ = load_volume(cgb_levelset)
    path_name = os.path.dirname(gwb_levelset)
    base_name = os.path.basename(gwb_levelset)
    split_name = base_name[:base_name.find('.')]

    cbstools.initVM()
    lamination=cbstools.LaminarVolumetricLayering()
    lamination.setDimensions(gwb_data.shape[0],gwb_data.shape[1],gwb_data.shape[2])
    lamination.setResolutions(im_header.get_zooms()[0],im_header.get_zooms()[1],im_header.get_zooms()[2])

    lamination.setInnerDistanceImage(cbstools.JArray('float')((gwb_data.flatten('F')).astype(float)))
    lamination.setOuterDistanceImage(cbstools.JArray('float')((cgb_data.flatten('F')).astype(float)))
    lamination.setNumberOfLayers(number_layers)
    lamination.setTopologyLUTdirectory(lut);
    lamination.execute()

    depth_data=np.reshape(np.array(lamination.getContinuousDepthMeasurement(),dtype=np.float32),gwb_data.shape,'F')
    layers_data=np.reshape(np.array(lamination.getDiscreteSampledLayers(),dtype=np.uint32),gwb_data.shape,'F')

    return layers_im, depth_im
    #save_volume(depth_data, im_header, im_affine,
    #            os.path.join(base_name + '_depth.nii.gz'))
    #save_volume(label_data, im_header, im_affine,
    #            os.path.join(base_name + '_profiles.nii.gz'))
