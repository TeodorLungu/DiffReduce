import nibabel as nib
import numpy as np
import vtk
from dash_vtk.utils import to_mesh_state, to_volume_state
from dipy.tracking.streamline import transform_streamlines
from scipy.interpolate import CubicSpline


def load_tck_file(
    tck_file_path,
    niigz_file_path,
    method="segment",
    cubic_spline=True,
    num_spline_points=50,
    show_volume=True,
):
    """
    Load the tck file and the niigz file and return the mesh state and volume state for visualization.
    """
    streamlines = load_streamlines(tck_file_path)
    if (
        show_volume
    ):  # Placeholder, since this is always true, but can be used to toggle volume visualization
        nii_img = nib.load(niigz_file_path)  # Load the NIfTI file
        data = nii_img.get_fdata()  # Get the data from the NIfTI file
        vtk_volume_data = volume_backend(data)  # Convert the data to VTK image data
        smoothFilter = smooth_filter_backend(
            vtk_volume_data
        )  # Apply a smoothing filter to the volume data
        # Transform streamlines to voxel coordinates (register in the same space as the volume data)
        streamlines_registered = transform_streamlines(
            streamlines, np.linalg.inv(nii_img.affine)
        )
        volumeState = to_volume_state(
            smoothFilter.GetOutput()
        )  # Convert the volume data to volume state
    else:
        streamlines_registered = streamlines  # Will never reach due to placeholder above, but can be used to toggle volume visualization

    points, lines, colors = vtk_structures_backend()  # Initialize the VTK structures

    if method == "segment":
        points, lines, colors = color_by_segment(
            streamlines_registered,
            cubic_spline,
            num_spline_points,
            points,
            lines,
            colors,
        )  # Color by segment
    elif method == "whole":
        points, lines, colors = color_by_whole(
            streamlines_registered,
            cubic_spline,
            num_spline_points,
            points,
            lines,
            colors,
        )  # Color by whole streamline
    else:
        raise ValueError(
            "Invalid method specified"
        )  # Raise an error if an invalid method is specified

    # do the VTK magic
    polyData = poly_data_backend(points, lines, colors)
    tubeFilter = tube_filter_backend(polyData)
    meshState = to_mesh_state(
        tubeFilter.GetOutput(), "Colors"
    )  # "Colors" is the name of the color array in the polydata, otherwise no colors :(
    return meshState, volumeState if show_volume else None


def load_streamlines(tck_file_path):
    """
    Load the streamlines from the tck file, using nibabel.
    """
    tck = nib.streamlines.load(tck_file_path)
    return tck.streamlines


def vtk_structures_backend():
    """
    Create the VTK structures for the streamlines.
    """
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)  # RGB
    colors.SetName("Colors")  # Name of the color array
    return points, lines, colors


def poly_data_backend(points, lines, colors):
    """
    Create the poly data for the streamlines, using the VTK structures.
    """
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(points)
    polyData.SetLines(lines)
    polyData.GetCellData().SetScalars(colors)
    return polyData


def volume_backend(data):
    # Create a VTK image data
    vtk_data = vtk.vtkImageData()
    vtk_data.SetDimensions(data.shape)
    vtk_data.AllocateScalars(vtk.VTK_DOUBLE, 1)

    # Copy the data from the NIfTI file to VTK image data
    for z in range(data.shape[2]):
        for y in range(data.shape[1]):
            for x in range(data.shape[0]):
                vtk_data.SetScalarComponentFromDouble(x, y, z, 0, data[x, y, z])

    return vtk_data


def smooth_filter_backend(vtk_volume_data):
    """
    Create a smoothing filter for the volume data
    """
    smooth_filter = vtk.vtkImageGaussianSmooth()
    smooth_filter.SetInputData(vtk_volume_data)
    smooth_filter.SetStandardDeviations(
        1.0, 1.0, 1.0
    )  # Adjust the standard deviations as needed
    smooth_filter.Update()

    return smooth_filter


def tube_filter_backend(polyData, radius=0.2, num_sides=10):
    """
    Adjust the radius and number of sides of the tube filter as needed
    bigger radius = thicker tubes (too big = tubes overlap and look like a single tube)
    more sides = smoother tubes (but more computationally expensive)
    """
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetInputData(polyData)  # Set the input data
    tubeFilter.SetRadius(radius)
    tubeFilter.SetNumberOfSides(num_sides)
    tubeFilter.CappingOn()  # Cap the ends of the tubes
    tubeFilter.Update()
    return tubeFilter


def color_by_segment(
    streamlines, cubic_spline, num_spline_points, points, lines, colors
):
    total_points = 0

    for streamline in streamlines:
        # Smooth the streamline using cubic spline interpolation (if specified)
        tck_smoothed = smooth_streamline(streamline, cubic_spline, num_spline_points)

        for i in range(len(tck_smoothed) - 1):
            point1 = tck_smoothed[i]  # Get the first point
            point2 = tck_smoothed[i + 1]  # Get the second point
            points.InsertNextPoint(point1.tolist())  # Add the first point to the points
            points.InsertNextPoint(
                point2.tolist()
            )  # Add the second point to the points

            line = vtk.vtkLine()  # Create a line, connecting the two points
            line.GetPointIds().SetId(0, total_points)  # Set the first point of the line
            line.GetPointIds().SetId(
                1, total_points + 1
            )  # Set the second point of the line
            lines.InsertNextCell(line)  # Add the line to the lines

            color = map_endpoint_to_color(point1, point2)  # Map the color to the line
            colors.InsertNextTypedTuple(color)  # Add the color to the colors

            total_points += 2  # Increment the total points, because we added two points

    return points, lines, colors


def color_by_whole(streamlines, cubic_spline, num_spline_points, points, lines, colors):
    total_points = 0
    for streamline in streamlines:
        tck_smoothed = smooth_streamline(
            streamline, cubic_spline, num_spline_points
        )  # Smooth the streamline
        color = map_endpoint_to_color(
            tck_smoothed[0], tck_smoothed[-1]
        )  # Map the color to the streamline, using the first and last points (whole streamline color)

        for i in range(len(tck_smoothed) - 1):
            # Same as color_by_segment, but with the same color for the whole streamline
            point1 = tck_smoothed[i]
            point2 = tck_smoothed[i + 1]
            points.InsertNextPoint(point1.tolist())
            points.InsertNextPoint(point2.tolist())

            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, total_points)
            line.GetPointIds().SetId(1, total_points + 1)
            lines.InsertNextCell(line)

            total_points += 2
            colors.InsertNextTypedTuple(color)

    return points, lines, colors


def smooth_streamline(streamline, cubic_spline, num_spline_points):
    # Convert the streamline to a numpy array
    streamline_np = np.array(streamline)
    # Apply cubic spline interpolation (if specified)
    if cubic_spline:
        cs = CubicSpline(np.arange(len(streamline_np)), streamline_np, axis=0)
        return cs(np.linspace(0, len(streamline_np) - 1, num_spline_points))
    else:
        # Return the original streamline, as numpy array
        return streamline_np


def map_endpoint_to_color(start_point, end_point, power=1):
    # Calculate the direction vector between the start and end points
    direction = np.array(end_point) - np.array(
        start_point
    )  # Calculate the direction vector
    if np.linalg.norm(direction) == 0:  # If the direction vector is zero (no movement)
        return np.array(
            [0, 0, 0], dtype=np.uint8
        )  # Return black if no direction (no movement).
    normalized_direction = np.abs(
        direction / np.linalg.norm(direction)
    )  # Use absolute value to ignore direction sign.
    accelerated_color = (
        normalized_direction**power
    )  # Apply power to accelerate fall-off
    color = (accelerated_color * 255).astype(np.uint8)  # Scale directly to [0, 255]
    return color
