def sample_volume(nii_file, vertices):
    '''Samples volumetric data on surface mesh vertices'''
    import numpy as np
    import nibabel as nb
    img = nb.load(nii_file)
#    img=image
    affine = img.get_affine()
    data = img.get_data()
    # for each vertex in the highres mesh find voxel it maps to
    dim = [affine[0, 0], affine[1, 1], affine[2, 2]]
    # might require -dim if axes are flipped. Consider try
    idx = np.asarray(np.round(vertices / dim), dtype='int64')
    data_mesh = data[idx[:, 0], idx[:, 1], idx[:, 2]]
    return data_mesh;

def generate_profiles(volumes, vertices):
    '''Creates intensity profiles for vertex coordinates in 4D volume'''
    import numpy as np
    n_samples=np.shape(volumes.get_data())[3]
    intensity_profiles=np.zeros([len(vertices),n_samples])
    affine = volumes.get_affine()
    dim = [affine[0, 0], affine[1, 1], affine[2, 2]]
    idx = np.asarray(np.round(vertices / dim), dtype='int64')
    for volume in range(n_samples):
        data = volumes.get_data()[:,:,:,volume]
        data_mesh = data[idx[:, 0], idx[:, 1], idx[:, 2]]
        intensity_profiles[:,volume]=data_mesh[:]
    return intensity_profiles;

def convert_mesh_voxel2mipav(mesh,volume):
    '''converts mesh coordinates from voxelspace to mipav space'''
    import numpy as np
    affine=volume.get_affine()
    dim = [affine[0, 0], affine[1, 1], affine[2, 2]]
#Get absolute as sometimes dim axes are flipped but voxel coordinates are always positive
    idx = np.absolute(np.asarray((mesh['coords'] / dim), dtype='float'))
    meshcoords=idx
    return meshcoords;
