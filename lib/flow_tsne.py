from fasttsne import fast_tsne
import numpy as np
from scipy.spatial import cKDTree as KDTree


def tsne(fdarray, new_label = 'tsne',  channels = None, transform = 'arcsinh', transform_coeff = 5, sample = 6000,
         verbose = False, backgate = True, perplexity = 30.):
    """Perform t-SNE/viSNE on the FlowData object
    
    """

    # If the user has not provided a list of channels to use, 
    # use the intersection of all isotope channels
    if channels is None:
        channel_set = []
        for fd in fdarray:
            channel_set.append(set(fd.isotopes))
        channels = list(set.intersection(*channel_set))
    
    # Make a copy of the data in files that we want    
    points = []
    for fd in fdarray:
        points.append(np.vstack([ fd[ch] for ch in channels ]).T)

    # transform
    if transform == 'arcsinh':
        for pts in points:
            # Apply the transform inplace to the data
            np.arcsinh(transform_coeff*pts, pts)
    
    # Randomly sample to reduce the number of points
    sample_masks = []
    for pts in points:
        if sample < pts.shape[0]:
            # If we have enough points to subsample
            sample_masks.append(np.random.choice(pts.shape[0], sample, replace = False))
        else:
            # Otherwise we add all the points
            sample_masks.append(np.array(range(pts.shape[0])))

    # Sample the points, and construct a large matrix
    sample_points = []
    for mask, pts in zip(sample_masks, points):
        sample_points.append(pts[mask,:])
    X = np.vstack(sample_points)

    # Perform t-SNE
    Y = fast_tsne(X, perplexity=perplexity)
    assert Y is not None, ('t-SNE failed to return') 

    # Split Y into a matrix for each dataset
    splits = np.cumsum( np.array([ mask.shape[0] for mask in sample_masks], dtype = int))
    Y_split = np.split(Y, splits, axis = 0)

    # now expand data to reassign these points back into the dataset
    tsne_coords = []
    for (pts, mask, Yspt) in zip(points, sample_masks, Y_split):
        npoints = pts.shape[0]
        Z = np.zeros((npoints, 2))*float('NaN')
        Z[mask,:] = Yspt
        tsne_coords.append(Z)

    # If a point didn't get sampled, place its t-SNE coordinates at its nearest 
    # neighbor.
    if backgate:
        kd = KDTree(X)
        # select points not assigned values with t-SNE
        for pts, mask, coords, j  in zip(points, sample_masks, tsne_coords, range(len(points))):
            nan_points = np.argwhere(np.isnan(coords[:,0]))            
            d,near = kd.query(pts[nan_points],1) 
            # convert back to coordinates on the whole dataset
            coords[nan_points, :] = Y[near,:]
            tsne_coords[j] = coords
    # add to data to FlowData structure
    for fd, coords in zip(fdarray, tsne_coords):
        fd[new_label+'1'] = coords[:,0]
        fd[new_label+'2'] = coords[:,1]
