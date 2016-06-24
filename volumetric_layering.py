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
import cbstoolsjcc
import os
from io_volume import load_volume, save_volume

def layering(gwb_levelset, cgb_levelset, lut_dir, n_layers=10,
             save_data=True, base_name=None):

    # load the data as well as filenames and headers for saving later
    gwb_data, im_header, im_affine = load_volume(gwb_levelset)
    cgb_data, _, _ = load_volume(cgb_levelset)

    if not base_name:
        dir_name = os.path.dirname(gwb_levelset)
        base_name = os.path.basename(gwb_levelset)
        base_name = base_name[:base_name.find('.')]

    cbstoolsjcc.initVM(initialheap='6000m', maxheap='6000m')
    lamination=cbstoolsjcc.LaminarVolumetricLayering()
    lamination.setDimensions(gwb_data.shape[0],gwb_data.shape[1],gwb_data.shape[2])
    zooms = [x.item() for x in im_header.get_zooms()]
    lamination.setResolutions(zooms[0], zooms[1], zooms[2])

    lamination.setInnerDistanceImage(cbstoolsjcc.JArray('float')((gwb_data.flatten('F')).astype(float)))
    lamination.setOuterDistanceImage(cbstoolsjcc.JArray('float')((cgb_data.flatten('F')).astype(float)))
    lamination.setNumberOfLayers(n_layers)
    lamination.setTopologyLUTdirectory(lut_dir);
    lamination.execute()

    depth_data=np.reshape(np.array(lamination.getContinuousDepthMeasurement(),dtype=np.float32),gwb_data.shape,'F')
    layer_data=np.reshape(np.array(lamination.getDiscreteSampledLayers(),dtype=np.uint32),gwb_data.shape,'F')

    boundary_len = lamination.getLayerBoundarySurfacesLength()
    boundary_data=np.reshape(np.array(lamination.getLayerBoundarySurfaces(),dtype=np.uint32),
                            (gwb_data.shape[0], gwb_data.shape[1], gwb_data.shape[2],
                             boundary_len),'F')

    if save_data:
        save_volume(os.path.join(dir_name, base_name+'_depth.nii.gz'),
                    depth_data, im_affine, header=im_header)
        save_volume(os.path.join(dir_name, base_name + '_layers.nii.gz'),
                    layer_data, im_affine, header=im_header)
        save_volume(os.path.join(dir_name, base_name + '_boundaries.nii.gz'),
                    boundary_data, im_affine, header=im_header)

    return depth_data, layer_data, boundary_data


def sampling(boundary_img, intensity_img, save_data=True, base_name=None):

    # load the data as well as filenames and headers for saving later
    boundary_data, im_header, im_affine = load_volume(boundary_img)
    intensity_data, _, _ = load_volume(intensity_img)

    if not base_name:
        dir_name = os.path.dirname(intensity_img)
        base_name = os.path.basename(intensity_img)
        base_name = base_name[:base_name.find('.')]

    cbstoolsjcc.initVM(initialheap='6000m', maxheap='6000m')

    sampler = cbstoolsjcc.LaminarProfileSampling()
    sampler.setIntensityImage(cbstoolsjcc.JArray('float')((intensity_data.flatten('F')).astype(float)))
    sampler.setProfileSurfaceImage(cbstoolsjcc.JArray('float')((boundary_data.flatten('F')).astype(float)))
    zooms = [x.item() for x in im_header.get_zooms()]
    sampler.setResolutions(zooms[0], zooms[1], zooms[2])
    sampler.setDimensions(boundary_data.shape)
    sampler.execute()

    profile_data= np.reshape(np.array(sampler.getProfileMappedIntensityImage(),
                             dtype=np.float32), boundary_data.shape,'F')

    if save_data:
        save_volume(os.path.join(dir_name, base_name+'_profiles.nii.gz'),
                    profile_data, im_affine, header=im_header)

    return profile_data


#def create_levelsets(tissue_classification):


#    cbstoolsjcc.SurfaceProbabilityToLevelset.setDimensions
#cbstoolsjcc.SurfaceProbabilityToLevelset.setProbabilityImage
#cbstoolsjcc.SurfaceProbabilityToLevelset.setResolutions
#cbstoolsjcc.SurfaceProbabilityToLevelset.setScale_mm
