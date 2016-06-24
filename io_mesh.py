import nibabel as nb
import numpy as np

# function to load mesh geometry
def load_mesh_geometry(surf_mesh):
    # if input is a filename, try to load it with nibabel
    if isinstance(surf_mesh, basestring):
        if (surf_mesh.endswith('orig') or surf_mesh.endswith('pial') or
                surf_mesh.endswith('white') or surf_mesh.endswith('sphere') or
                surf_mesh.endswith('inflated')):
            coords, faces = nibabel.freesurfer.io.read_geometry(surf_mesh)
        elif surf_mesh.endswith('gii'):
            coords, faces = gifti.read(surf_mesh).getArraysFromIntent(nibabel.nifti1.intent_codes['NIFTI_INTENT_POINTSET'])[0].data, \
                            gifti.read(surf_mesh).getArraysFromIntent(nibabel.nifti1.intent_codes['NIFTI_INTENT_TRIANGLE'])[0].data
        elif surf_mesh.endswith('vtk'):
            coords, faces, _ = read_vtk(surf_mesh)
        elif surf_mesh.endswith('ply'):
            coords, faces = read_ply(surf_mesh)
        elif surf_mesh.endswith('obj'):
            coords, faces = read_obj(surf_mesh)
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
def load_mesh_data(surf_data, gii_darray=0):
    # if the input is a filename, load it
    if isinstance(surf_data, basestring):
        if (surf_data.endswith('nii') or surf_data.endswith('nii.gz') or
                surf_data.endswith('mgz')):
            data = np.squeeze(nibabel.load(surf_data).get_data())
        elif (surf_data.endswith('curv') or surf_data.endswith('sulc') or
                surf_data.endswith('thickness')):
            data = nibabel.freesurfer.io.read_morph_data(surf_data)
        elif surf_data.endswith('annot'):
            data = nibabel.freesurfer.io.read_annot(surf_data)[0]
        elif surf_data.endswith('label'):
            data = nibabel.freesurfer.io.read_label(surf_data)
        # check if this works with multiple indices (if dim(data)>1)
        elif surf_data.endswith('gii'):
            data = gifti.read(surf_data).darrays[gii_darray].data
        elif surf_data.endswith('vtk'):
            _, _, data = read_vtk(surf_data)
        else:
            raise ValueError('Format of data file not recognized.')
    elif isinstance(surf_data, np.ndarray):
        data = np.squeeze(surf_data)
    return data


# function to read vtk files
# ideally use pyvtk, but it didn't work for our data, look into why
def read_vtk(file):
    '''
    Reads ASCII coded vtk files using pandas,
    returning vertices, faces and data as three numpy arrays.
    '''
    import pandas as pd
    import csv
    # read full file while dropping empty lines
    try:
        vtk_df=pd.read_csv(file, header=None, engine='python')
    except csv.Error:
        raise ValueError('This vtk file appears to be binary coded currently only ASCII coded vtk files can be read')
    vtk_df=vtk_df.dropna()
    # extract number of vertices and faces
    number_vertices=int(vtk_df[vtk_df[0].str.contains('POINTS')][0].iloc[0].split()[1])
    number_faces=int(vtk_df[vtk_df[0].str.contains('POLYGONS')][0].iloc[0].split()[1])
    # read vertices into df and array
    start_vertices= (vtk_df[vtk_df[0].str.contains('POINTS')].index.tolist()[0])+1
    vertex_df=pd.read_csv(file, skiprows=range(start_vertices), nrows=number_vertices, sep='\s*', header=None, engine='python')
    if np.array(vertex_df).shape[1]==3:
        vertex_array=np.array(vertex_df)
    # sometimes the vtk format is weird with 9 indices per line, then it has to be reshaped
    elif np.array(vertex_df).shape[1]==9:
        vertex_df=pd.read_csv(file, skiprows=range(start_vertices), nrows=int(number_vertices/3)+1, sep='\s*', header=None, engine='python')
        vertex_array=np.array(vertex_df.iloc[0:1,0:3])
        vertex_array=np.append(vertex_array, vertex_df.iloc[0:1,3:6], axis=0)
        vertex_array=np.append(vertex_array, vertex_df.iloc[0:1,6:9], axis=0)
        for row in range(1,(int(number_vertices/3)+1)):
            for col in [0,3,6]:
                vertex_array=np.append(vertex_array, np.array(vertex_df.iloc[row:(row+1),col:(col+3)]),axis=0)
        # strip rows containing nans
        vertex_array=vertex_array[ ~np.isnan(vertex_array) ].reshape(number_vertices,3)
    else:
        print "vertex indices out of shape"
    # read faces into df and array
    start_faces= (vtk_df[vtk_df[0].str.contains('POLYGONS')].index.tolist()[0])+1
    face_df=pd.read_csv(file, skiprows=range(start_faces), nrows=number_faces, sep='\s*', header=None, engine='python')
    face_array=np.array(face_df.iloc[:,1:4])
    # read data into df and array if exists
    if vtk_df[vtk_df[0].str.contains('POINT_DATA')].index.tolist()!=[]:
        start_data=(vtk_df[vtk_df[0].str.contains('POINT_DATA')].index.tolist()[0])+3
        number_data = number_vertices
        data_df=pd.read_csv(file, skiprows=range(start_data), nrows=number_data, sep='\s*', header=None, engine='python')
        data_array=np.array(data_df)
    else:
        data_array = np.empty(0)

    return vertex_array, face_array, data_array

# function to read ASCII coded ply file
def read_ply(file):
    import pandas as pd
    import csv
    # read full file and drop empty lines
    try:
        ply_df = pd.read_csv(file, header=None, engine='python')
    except csv.Error:
        raise ValueError('This ply file appears to be binary coded currently only ASCII coded ply files can be read')
    ply_df = ply_df.dropna()
    # extract number of vertices and faces, and row that marks the end of header
    number_vertices = int(ply_df[ply_df[0].str.contains('element vertex')][0].iloc[0].split()[2])
    number_faces = int(ply_df[ply_df[0].str.contains('element face')][0].iloc[0].split()[2])
    end_header = ply_df[ply_df[0].str.contains('end_header')].index.tolist()[0]
    # read vertex coordinates into dict
    vertex_df = pd.read_csv(file, skiprows=range(end_header + 1),
                            nrows=number_vertices, sep='\s*', header=None,
                            engine='python')
    vertex_array = np.array(vertex_df)
    # read face indices into dict
    face_df = pd.read_csv(file, skiprows=range(end_header + number_vertices + 1),
                          nrows=number_faces, sep='\s*', header=None,
                          engine='python')
    face_array = np.array(face_df.iloc[:, 1:4])

    return vertex_array, face_array


def read_obj(file):
    def chunks(l,n):
      """Yield n-sized chunks from l"""
      for i in xrange(0, len(l), n):
          yield l[i:i+n]
    def indices(lst,element):
        result=[]
        offset = -1
        while True:
            try:
                offset=lst.index(element,offset+1)
            except ValueError:
                return result
            result.append(offset)
    fp=open(file,'r')
    n_vert=[]
    n_poly=[]
    k=0
    Polys=[]
	# Find number of vertices and number of polygons, stored in .obj file.
	#Then extract list of all vertices in polygons
    for i, line in enumerate(fp):
         if i==0:
    	#Number of vertices
             n_vert=int(line.split()[6])
             XYZ=np.zeros([n_vert,3])
         elif i<n_vert:
             XYZ[i-1]=map(float,line.split())
         elif i==2*n_vert+3:
             n_poly=int(line)
         elif i>2*n_vert+5:
             if not line.strip():
                 k=1
             elif k==1:
                 Polys.extend(line.split())
    Polys=map(int,Polys)
    npPolys=np.array(Polys)
    triangles=list(chunks(Polys,3))
    return XYZ, triangles;


