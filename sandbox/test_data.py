import matplotlib.pyplot as plt
import numpy as np  # linear algebra
import scipy
import scipy.ndimage
import data_transforms
import pathfinder
import utils
import utils_lung
import logger
import sys


def resample(image, spacing, new_spacing=[1, 1, 1]):
    # Determine current pixel spacing
    spacing = np.array(spacing)
    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)
    return image, new_spacing


def plot_2d(image3d, axis, pid, img_dir):
    fig = plt.figure()
    fig.canvas.set_window_title(pid)
    ax = fig.add_subplot(111)
    idx = image3d.shape[axis] / 2
    if axis == 0:  # sax
        ax.imshow(image3d[idx, :, :], cmap=plt.cm.gray)
    if axis == 1:  # 2 lungs
        ax.imshow(image3d[:, idx, :], cmap=plt.cm.gray)
    if axis == 2:  # side view
        ax.imshow(image3d[:, :, idx], cmap=plt.cm.gray)
    fig.savefig(img_dir + '/%s.png' % pid, bbox_inches='tight')
    fig.clf()
    plt.close('all')


def test1():
    image_dir = utils.get_dir_path('analysis', pathfinder.METADATA_PATH)
    image_dir = image_dir + '/test_1/'
    utils.automakedir(image_dir)

    sys.stdout = logger.Logger(image_dir + '/%s.log' % 'test1_log')
    sys.stderr = sys.stdout

    patient_data_paths = utils_lung.get_patient_data_paths(pathfinder.DATA_PATH)
    print len(patient_data_paths)

    for k, p in enumerate(patient_data_paths):
        pid = utils_lung.extract_pid(p)
        try:
            sid2data, sid2metadata = utils_lung.get_patient_data(p)
            sids_sorted = utils_lung.sort_slices_plane(sid2metadata)
            sids_sorted_jonas = utils_lung.sort_slices_jonas(sid2metadata)
            sid2position = utils_lung.slice_location_finder(sid2metadata)

            try:
                slice_thickness_pos = np.abs(sid2metadata[sids_sorted[0]]['ImagePositionPatient'][2] -
                                             sid2metadata[sids_sorted[1]]['ImagePositionPatient'][2])
            except:
                print 'This patient has no ImagePosition!'
                slice_thickness_pos = 0.
            try:
                slice_thickness_loc = np.abs(
                    sid2metadata[sids_sorted[0]]['SliceLocation'] - sid2metadata[sids_sorted[1]]['SliceLocation'])
            except:
                print 'This patient has no SliceLocation!'
                slice_thickness_loc = 0.

            jonas_slicethick = []
            for i in xrange(len(sids_sorted_jonas) - 1):
                s = np.abs(sid2position[sids_sorted_jonas[i + 1]] - sid2position[sids_sorted_jonas[i]])
                jonas_slicethick.append(s)

            full_img = np.stack([data_transforms.ct2HU(sid2data[sid], sid2metadata[sid]) for sid in sids_sorted])
            del sid2data, sid2metadata
            # spacing = sid2metadata[sids_sorted[0]]['PixelSpacing']
            # spacing = [slice_thickness, spacing[0], spacing[1]]
            # resampled_image, _ = resample(full_img, spacing)
            plot_2d(full_img, axis=0, pid=pid + 'ax0', img_dir=image_dir)
            plot_2d(full_img, axis=1, pid=pid + 'ax1', img_dir=image_dir)
            plot_2d(full_img, axis=2, pid=pid + 'ax2', img_dir=image_dir)
            print k, pid, full_img.shape, slice_thickness_pos, slice_thickness_loc, set(jonas_slicethick)
            del full_img
            # utils.save_pkl(data_dict, image_dir + '/test1_log.pkl')
        except:
            print 'exception!!!', pid


if __name__ == '__main__':
    test1()
