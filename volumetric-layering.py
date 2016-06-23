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

parser = argparse.ArgumentParser(description='This program does something!')
parser.add_argument('-g','--gwb', type=str, help='input GM/WM boundary level set (.nii or .nii.gz)')
parser.add_argument('-c','--cgb', type=str, help='input CSF/GM boundary level set (.nii or .nii.gz)')
parser.add_argument('-l','--layers',help='number of intra-cortical layers',type=int,default=10)

args=parser.parse_args()

gwb=nb.load(args.gwb)
cgb=nb.load(args.cgb)

gwb_data=gwb.get_data()
cgb_data=cgb.get_data()

# needed for clean outputs
im_name=os.path.basename(gwb.get_filename())
pre_name=im_name[0:im_name.find('.')]
im_aff=gwb.affine

lutfiles='/home/pilou/Code/github/cbstools/atlases/lookuptables'

cbstools.initVM()
lamination=cbstools.LaminarVolumetricLayering()
lamination.setDimensions(gwb.shape[0],gwb.shape[1],gwb.shape[2])
lamination.setResolutions(gwb.header.getZooms()[0],gwb.header.getZooms()[1],gwb.header.getZooms()[2])

## to check: what is the ordering of the x,y,z dimensions??

## numpy uses z+nx*y+nx*ny*x ordering, we do x+nx*y+nx*ny*z :(
## -> check 'swapaxes', 'reshape', 'flatten' functions

lamination.setInnerDistanceImage(cbstools.JArray('float')((gwb_data.flatten('F')).astype(float)))
lamination.setOuterDistanceImage(cbstools.JArray('float')((cgb_data.flatten('F')).astype(float)))

lamination.setNumberOfLayers(args.layers)

lamination.setTopologyLUTdirectory('/home/pilou/Code/github/cbstools/de/mpg/cbs/structures/');
#mgdm.setTopology('no');

lamination.execute()

# output: need to recast types, check for proper ordering??
depth_im=np.reshape(np.array(lamination.getContinuousDepthMeasurement(),dtype=np.float32),gwb_data.shape,'F')

label_im=np.reshape(np.array(lamination.getDiscreteSampledLayers(),dtype=np.uint32),gwb_data.shape,'F')

# save
out_im=nb.Nifti1Image(depth_im,im_aff)
nb.save(out_im,pre_name+'_depth.nii.gz')
out_im=nb.Nifti1Image(label_im,im_aff)
nb.save(out_im,pre_name+'_labels.nii.gz')

