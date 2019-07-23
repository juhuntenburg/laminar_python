# adapt the output so that files can also be saved in other formats than nifti
import argparse
import numpy as np
import nibabel as nb
import cbstools
import os
from io_volume import load_volume, save_volume
from io_mesh import load_mesh_geometry, save_mesh_geometry


def create_levelsets(tissue_prob_img, save_data=True, base_name=None):

    '''
    Creates levelset surface representations from a tissue classification.

        Parameters
        -----------
        tissue_prob_img : Tissue segmentation to be turned into levelset.
            Either a binary tissue classfication with value 1 inside and 0
            outside the to-be-created surface, or ????
            Can be a path to a Nifti file or Nibabel image object.
        save_data : Whether the output levelset image should be saved
            (default is 'True').
        base_name : If save_data is set to True, this parameter can be used to
            specify where the output should be saved. Thus can be the path to a
            directory or a full filename. The suffix 'levelset' will be added
            to the filename. If None (default), the output will be saved to the
            current directory.

        Returns
        -------
        Levelset representation of surface as Nibabel image object
    '''

    # load the data as well as filenames and headers for saving later
    prob_img = load_volume(tissue_prob_img)
    prob_data = prob_img.get_data()
    hdr = prob_img.get_header()
    aff = prob_img.get_affine()

    try:
        cbstools.initVM(initialheap='6000m', maxheap='6000m')
    except ValueError:
        pass

    prob2level = cbstools.SurfaceProbabilityToLevelset()

    prob2level.setProbabilityImage(cbstools.JArray('float')((prob_data.flatten('F')).astype(float)))
    prob2level.setDimensions(prob_data.shape)
    zooms = [x.item() for x in hdr.get_zooms()]
    prob2level.setResolutions(zooms[0], zooms[1], zooms[2])
    prob2level.execute()

    levelset_data = np.reshape(np.array(prob2level.getLevelSetImage(),
                               dtype=np.float32), prob_data.shape, 'F')

    levelset_img = nb.Nifti1Image(levelset_data, aff, hdr)

    if save_data:
        if base_name:
            base_name += '_'
        else:
            if not isinstance(tissue_prob_img, basestring):
                base_name = os.getcwd() + '/'
                print "saving to %s" % base_name
            else:
                dir_name = os.path.dirname(tissue_prob_img)
                base_name = os.path.basename(tissue_prob_img)
                base_name = os.path.join(dir_name,
                                         base_name[:base_name.find('.')]) + '_'

        save_volume(base_name+'levelset.nii.gz', levelset_img)

    return levelset_img


def layering(gwb_levelset, cgb_levelset, n_layers=10, lut_dir='lookuptables/',
             save_data=True, base_name=None):

    '''
    Equivolumetric layering of the cortical sheet.

    Waehnert et al. (2014). Anatomically motivated modeling of cortical
    laminae. http://doi.org/10.1016/j.neuroimage.2013.03.078

        Parameters
        -----------
        gwb_levelset : Levelset representation of the GM/WM surface. Can be
            created from tissue segmentation with the "create_levelsets"
            function. Can be path to a Nifti file or Nibabel image object.
        cgb_levelset : Levelset representation of the CSF/GM surface. Can be
            created from tissue segmentation with the "create_levelsets"
            function. Can be path to a Nifti file or Nibabel image object.
        n_layers : int, number of layers to be created.
        lut_dir : Path to directory with lookup tables. Default is to search it
            within this directory.
        save_data : Whether the output layer image should be saved
            (default is 'True').
        base_name : If save_data is set to True, this parameter can be used to
            specify where the output should be saved. Thus can be the path to a
            directory or a full filename. The suffixes 'depth', 'layers' and
            'boundaries' will be added to the respective outputs. If None
            (default), the output will be saved to the current directory.

        Returns
        -------
        Three Nibabel image objects :
            Continuous depth from 0(WM) to 1(CSF)
            Discrete layers from 1(bordering WM) to n_layers(bordering CSF)
            Levelset representations of boundaries between layers (4D)
    '''

    # load the data as well as filenames and headers for saving later
    gwb_img = load_volume(gwb_levelset)
    gwb_data = gwb_img.get_data()
    hdr = gwb_img.get_header()
    aff = gwb_img.get_affine()

    cgb_data = load_volume(cgb_levelset).get_data()

    try:
        cbstools.initVM(initialheap='6000m', maxheap='6000m')
    except ValueError:
        pass

    lamination = cbstools.LaminarVolumetricLayering()
    lamination.setDimensions(gwb_data.shape[0], gwb_data.shape[1], gwb_data.shape[2])
    zooms = [x.item() for x in hdr.get_zooms()]
    lamination.setResolutions(zooms[0], zooms[1], zooms[2])

    lamination.setInnerDistanceImage(cbstools.JArray('float')((gwb_data.flatten('F')).astype(float)))
    lamination.setOuterDistanceImage(cbstools.JArray('float')((cgb_data.flatten('F')).astype(float)))
    lamination.setNumberOfLayers(n_layers)
    lamination.setTopologyLUTdirectory(lut_dir)
    lamination.execute()

    depth_data=np.reshape(np.array(lamination.getContinuousDepthMeasurement(), dtype=np.float32),gwb_data.shape,'F')
    layer_data=np.reshape(np.array(lamination.getDiscreteSampledLayers(), dtype=np.uint32),gwb_data.shape,'F')

    boundary_len = lamination.getLayerBoundarySurfacesLength()
    boundary_data=np.reshape(np.array(lamination.getLayerBoundarySurfaces(), dtype=np.float32),
                             (gwb_data.shape[0], gwb_data.shape[1],
                              gwb_data.shape[2],
                              boundary_len), 'F')

    depth_img = nb.Nifti1Image(depth_data, aff, hdr)
    layer_img = nb.Nifti1Image(layer_data, aff, hdr)
    boundary_img = nb.Nifti1Image(boundary_data, aff, hdr)

    if save_data:
        if base_name:
            base_name += '_'
        else:
            if not isinstance(gwb_levelset, basestring):
                base_name = os.getcwd() + '/'
                print "saving to %s" % base_name
            else:
                dir_name = os.path.dirname(gwb_levelset)
                base_name = os.path.basename(gwb_levelset)
                base_name = os.path.join(dir_name,
                                         base_name[:base_name.find('.')]) + '_'

        save_volume(base_name + 'depth.nii.gz', depth_img)
        save_volume(base_name + 'layers.nii.gz', layer_img)
        save_volume(base_name + 'boundaries.nii.gz', boundary_img)

    return depth_img, layer_img, boundary_img


def profile_sampling(boundary_img, intensity_img,
                     save_data=True, base_name=None):

    '''
    Sampling data on multiple intracortical layers.

        Parameters
        -----------
        boundary_img : Levelset representations of different intracortical
            layers in a 4D image (4th dimensions representing the layers).
            Can be created from GM and WM leveset with the "layering" function.
            Can be path to a Nifti file or Nibabel image object.
        intensity_img : Image from which data should be sampled. Can be path to
            a Nifti file or Nibabel image object.
        save_data : Whether the output profile image should be saved
            (default is 'True').
        base_name : If save_data is set to True, this parameter can be used to
            specify where the output should be saved. Thus can be the path to a
            directory or a full filename. The suffix 'profiles' will be added
            to filename. If None (default), the output will be saved to the
            current directory.

        Returns
        -------
        Nibabel image object (4D), where the 4th dimension represents the
        different cortical surfaces, i.e. the profile for each voxel in the
        3D space.
    '''

    # load the data as well as filenames and headers for saving later
    boundary_img = load_volume(boundary_img)
    boundary_data = boundary_img.get_data()
    hdr = boundary_img.get_header()
    aff = boundary_img.get_affine()

    intensity_data = load_volume(intensity_img).get_data()

    try:
        cbstools.initVM(initialheap='6000m', maxheap='6000m')
    except ValueError:
        pass

    sampler = cbstools.LaminarProfileSampling()
    sampler.setIntensityImage(cbstools.JArray('float')((intensity_data.flatten('F')).astype(float)))
    sampler.setProfileSurfaceImage(cbstools.JArray('float')((boundary_data.flatten('F')).astype(float)))
    zooms = [x.item() for x in hdr.get_zooms()]
    sampler.setResolutions(zooms[0], zooms[1], zooms[2])
    sampler.setDimensions(boundary_data.shape)
    sampler.execute()

    profile_data = np.reshape(np.array(sampler.getProfileMappedIntensityImage(),
                              dtype=np.float32), boundary_data.shape,'F')

    profile_img = nb.Nifti1Image(profile_data, aff, hdr)

    if save_data:
        if base_name:
            base_name += '_'
        else:
            if not isinstance(intensity_img, basestring):
                base_name = os.getcwd() + '/'
                print "saving to %s" % base_name
            else:
                dir_name = os.path.dirname(intensity_img)
                base_name = os.path.basename(intensity_img)
                base_name = os.path.join(dir_name,
                                         base_name[:base_name.find('.')]) + '_'
        save_volume(base_name+'profiles.nii.gz', profile_img)

    return profile_img


# There is something wrong with this, all the created surfaces have the same
# vertex coordinates
def profile_meshing(profile_file, surf_mesh, save_data=True, base_name=None):

    '''
    Converting the levelset representation of multiple intracorticle surfaces
    into multiple surface meshes.

        Parameters
        -----------
        profile_file : Levelset representations of different intracortical
            layers in a 4D image (4th dimensions representing the layers).
            Can be created from GM and WM leveset with the "layering" function.
            Can be path to a Nifti file or Nibabel image object.
        surf_mesh : Original surface mesh serving as a reference for the
                    topology of all intracortical surfaces.
        save_data : Whether the output meshes should be saved
            (default is 'True').
        base_name : If save_data is set to True, this parameter can be used to
            specify where the output should be saved. Thus can be the path to a
            directory or a full filename. A suffix indicating the number of the
            layer will be added. If None (default), the output will be saved to
            the current directory.

        Returns
        -------
        A list of intracortical surface meshes, each represented as a
        dictionary with entries 'coords' and 'faces'
    '''

    profile_img = load_volume(profile_file)
    profile_data = profile_img.get_data()
    profile_len = profile_data.shape[3]
    hdr = profile_img.get_header()
    aff = profile_img.get_affine()

    in_coords = load_mesh_geometry(surf_mesh)['coords']
    in_faces = load_mesh_geometry(surf_mesh)['faces']

    try:
        cbstools.initVM(initialheap='6000m', maxheap='6000m')
    except ValueError:
        pass

    mesher = cbstools.LaminarProfileMeshing()

    mesher.setDimensions(profile_data.shape)
    zooms = [x.item() for x in hdr.get_zooms()]
    mesher.setResolutions(zooms[0], zooms[1], zooms[2])

    mesher.setProfileSurfaceImage(cbstools.JArray('float')((profile_data.flatten('F')).astype(float)))
    mesher.setInputSurfacePoints(cbstools.JArray('float')(in_coords.flatten().astype(float)))
    mesher.setInputSurfaceTriangles(cbstools.JArray('int')(in_faces.flatten().astype(int)))

    mesher.execute()

    out_coords = np.zeros((in_coords.shape[0], in_coords.shape[1], profile_len))
    out_faces = np.zeros((in_faces.shape[0], in_faces.shape[1], profile_len))

    mesh_list = []
    for i in range(profile_len):
        current_mesh = {}
        current_mesh['coords'] = np.reshape(np.array(mesher.getSampledSurfacePoints(i),
                                            dtype=np.float32),in_coords.shape)
        current_mesh['faces'] =  np.reshape(np.array(mesher.getSampledSurfaceTriangles(i),
                                            dtype=np.float32),in_faces.shape)
        mesh_list.append(current_mesh)

    if save_data:
        if base_name:
            base_name += '_'
        else:
            if not isinstance(profile_file, basestring):
                base_name = os.getcwd() + '/'
                print "saving to %s" % base_name
            else:
                dir_name = os.path.dirname(intensity_img)
                base_name = os.path.basename(intensity_img)
                base_name = os.path.join(dir_name,
                                         base_name[:base_name.find('.')]) + '_'

        for i in range(len(mesh_list)):
            save_mesh_geometry(base_name + '%s.vtk' % str(i), mesh_list[i])

    return mesh_list
