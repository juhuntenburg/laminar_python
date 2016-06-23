import nibabel as nb

# function to read volumetric tissue classification and turn it into 1D array


# function to load mesh geometry
def load_geometry(surf_mesh):
    # if input is a filename, try to load it
    if isinstance(surf_mesh, _basestring):
        if (surf_mesh.endswith('orig') or surf_mesh.endswith('pial') or
                surf_mesh.endswith('white') or surf_mesh.endswith('sphere') or
                surf_mesh.endswith('inflated')):
            coords, faces = nibabel.freesurfer.io.read_geometry(surf_mesh)
        elif surf_mesh.endswith('gii'):
            coords, faces = gifti.read(surf_mesh).getArraysFromIntent(nibabel.nifti1.intent_codes['NIFTI_INTENT_POINTSET'])[0].data, \
                            gifti.read(surf_mesh).getArraysFromIntent(nibabel.nifti1.intent_codes['NIFTI_INTENT_TRIANGLE'])[0].data
        # if a dictionary is given, check it contains entries for coords and faces
        elif isinstance(surf_mesh, dict):
            if ('faces' in surf_mesh and 'coords' in surf_mesh):
                coords, faces = surf_mesh['coords'], surf_mesh['faces']
            else:
                raise ValueError('If surf_mesh is given as a dictionary it must '
                                 'contain items with keys "coords" and "faces"')
        else:
            raise ValueError('surf_mesh must be a either filename or a dictionary '
                             'containing items with keys "coords" and "faces"')
    return coords, faces


# function to load mesh data


# function to make 1D arrays from meshes geometry and data
