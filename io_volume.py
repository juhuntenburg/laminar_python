import nibabel as nb
import numpy as np

# function to read volumetric tissue classification and turn into 3D array
def load_volume(mri_vol):
  # if input is a filename, try to load it
    if isinstance(mri_vol, basestring):
  # importing nifti files
        if (mri_vol.endswith('nii') or mri_vol.endswith('nii.gz')):
           img=nb.load(mri_vol)
           img_data=np.array(img.get_data())
           img_affine=img.get_affine()
           img_header=img.get_header()
   # importing mnc files using pyminc, suggest to download if missing
        elif mri_vol.endswith('mnc'):
            try:
                img=nb.minc2.load(mri_vol)
                img_data=np.array(img.get_data())
                img_affine=img.get_affine()
                img_header=img.get_header()
            except ValueError:
                print "loading .mnc files requires h5py, try installing with:"
                print '"sudo pip install h5py"'
   # option to add in more file types here, eg analyze
   # if volume is already an np array
#    elif isinstance(mri_vol,np.ndarray):
#         img_data=np.array(mri_vol)
    else:
            raise ValueError('volume must be a either filename or a numpy array')
    return img_data, img_header, img_affine;
