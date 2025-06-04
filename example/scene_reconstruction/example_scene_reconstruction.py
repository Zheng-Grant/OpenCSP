from os.path import join, dirname, abspath
import sys
import numpy as np
sys.path.append(abspath(join(dirname(__file__), '..', '..')))


from opencsp.app.scene_reconstruction.lib.SceneReconstruction import SceneReconstruction
from opencsp.app.scene_reconstruction.lib.SceneReconstruction_no_aruco import SceneReconstructionNoAruco
from opencsp.common.lib.camera.Camera import Camera
from opencsp.common.lib.geometry.Vxyz import Vxyz
from opencsp.common.lib.opencsp_path.opencsp_root_path import opencsp_code_dir
import opencsp.common.lib.tool.file_tools as ft
import opencsp.common.lib.tool.log_tools as lt




def scene_reconstruction(dir_output, dir_input):

    # TODO: remove the dependency on AruCO markers

    """
    Reconstructs the XYZ locations of Aruco markers in a scene.

    Parameters
    ----------
    dir_output : str
        The directory where the output files, including point locations and calibration figures, will be saved.
    dir_input : str
        The directory containing the input files needed for scene reconstruction. This includes:

        - 'camera.h5': HDF5 file containing camera parameters.
        - 'known_point_locations.csv': CSV file with known point locations.
        - 'aruco_marker_images/NAME.JPG': Directory containing images of Aruco markers.
        - 'point_pair_distances.csv': CSV file with distances between point pairs.
        - 'alignment_points.csv': CSV file with alignment points.

    Notes
    -----
    This function performs the following steps:

    1. Loads the camera parameters from an HDF5 file.
    2. Loads known point locations, point pair distances, and alignment points from CSV files.
    3. Initializes the SceneReconstruction object with the camera parameters and known point locations.
    4. Runs the calibration process to determine the marker positions.
    5. Scales the points based on the provided point pair distances.
    6. Aligns the points using the provided alignment points.
    7. Saves the reconstructed point locations to a CSV file.
    8. Saves calibration figures as PNG files in the output directory.

    Examples
    --------
    >>> scene_reconstruction('/path/to/output', '/path/to/input')

    """
    # "ChatGPT 4o" assisted with generating this docstring.

    # Load components
    camera = Camera.load_from_hdf(join(dir_input, 'camera.h5'))
    known_point_locations = np.loadtxt(join(dir_input, 'known_point_locations.csv'), delimiter=',', skiprows=1)
    image_filter_path = join(dir_input, 'aruco_marker_images', '*.JPG')
    point_pair_distances = np.loadtxt(join(dir_input, 'point_pair_distances.csv'), delimiter=',', skiprows=1)
    alignment_points = np.loadtxt(join(dir_input, 'alignment_points.csv'), delimiter=',', skiprows=1)

    # TODO: Test block for no aruco scene reconstruction
    marked_points_path = join(dir_input, '_test_aruco_free_data/pseudo_markers_full.xlsx')
    cal_scene_recon = SceneReconstructionNoAruco(camera, known_point_locations, image_filter_path, marked_points_path=marked_points_path)
    cal_scene_recon.make_figures = True
    cal_scene_recon.run_calibration()

    # Perform marker position calibration
    cal_scene_recon = SceneReconstruction(camera, known_point_locations, image_filter_path)
    cal_scene_recon.make_figures = True
    cal_scene_recon.run_calibration()

    # Scale points
    point_pairs = point_pair_distances[:, :2].astype(int)
    distances = point_pair_distances[:, 2]
    cal_scene_recon.scale_points(point_pairs, distances)

    # Align points
    marker_ids = alignment_points[:, 0].astype(int)
    alignment_values = Vxyz(alignment_points[:, 1:4].T)
    cal_scene_recon.align_points(marker_ids, alignment_values)

    # Save points as CSV
    cal_scene_recon.save_data_as_csv(join(dir_output, 'point_locations.csv'))

    # Save calibrtion figures
    for fig in cal_scene_recon.figures:
        fig.savefig(join(dir_output, fig.get_label() + '.png'))


def example_driver(dir_output_fixture, dir_input_fixture):

    dir_input = join(opencsp_code_dir(), 'app/scene_reconstruction/test/data/data_measurement')
    dir_output = join(dirname(__file__), 'data/output/scene_reconstruction')
    if dir_input_fixture:
        dir_input = dir_input_fixture
    if dir_output_fixture:
        dir_output = dir_input_fixture

    # Define output directory
    ft.create_directories_if_necessary(dir_input)

    # Set up logger
    lt.logger(join(dir_output, 'log.txt'), lt.log.INFO)

   
    scene_reconstruction(dir_output, dir_input)


if __name__ == '__main__':
    example_driver(None, None)
