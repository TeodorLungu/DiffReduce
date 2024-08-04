import os

from PIL import Image

from constants import BASE_DIR_FALLBACK, BASE_DIR_FULL, MAPPING_DICT


def get_tck_file_path(patient_id, bundle_name):
    """
    Get the path to the tck file for a given patient and bundle name.
    """
    if bundle_name is None or patient_id is None:
        return ""
    file_path = os.path.join(
        BASE_DIR_FULL,
        f"sub-{patient_id}/TOM_trackings/{bundle_name}.tck",  # Modify if folder structure is different
    )
    if not os.path.isfile(file_path):
        file_path = os.path.join(
            BASE_DIR_FALLBACK, f"Patient_0/TOM_trackings/{bundle_name}.tck"
        )  # Modify if folder structure is different

    return file_path


def get_niigz_file_path(patient_id):
    """
    Get the path to the .nii.gz file for a given patient. (this is the volume data file, unique for each patient, no bundle name needed)
    """
    if patient_id is None:
        return ""
    file_path = os.path.join(
        BASE_DIR_FULL,
        f"sub-{patient_id}/dti__FA.nii.gz",  # Modify if folder structure is different
    )
    if not os.path.isfile(file_path):
        file_path = os.path.join(
            BASE_DIR_FALLBACK, f"Patient_0/100206__fa.nii.gz"
        )  # Modify if folder structure is different

    return file_path


def get_image_url(category, patient_id, axis_value, width, height):
    """
    Get the image URL for a given category, patient ID, and axis value (i.e., axial_inferior, axial_superior, etc.)
    """
    if category is None:
        return ""
    axis_raw_value = MAPPING_DICT.get(axis_value)
    # First try to see if real data exists for the patient
    image_folder = (
        f"sub-{patient_id}/Screenshots/"  # Modify if folder structure is different
    )
    image_name = (
        f"{category}_{axis_raw_value}.png"  # Modify if folder structure is different
    )
    image_path = os.path.join(BASE_DIR_FULL, image_folder, image_name)

    # Load image with pillow
    try:
        # Open the image
        im = Image.open(image_path).convert("RGB")  # Convert to RGB
        im_resized = im.resize((width, height))  # Resize the image
    # If the image does not exist, load the default image folder
    except:
        image_folder = (
            f"Patient_0/Screenshots/"  # Modify if folder structure is different
        )
        image_name = f"{category}_{axis_raw_value}.png"  # Modify if folder structure is different
        # Get the path to the image
        image_path = os.path.join(BASE_DIR_FALLBACK, image_folder, image_name)
        im = Image.open(image_path).convert("RGB")
        im_resized = im.resize((width, height))

    return im_resized


def list_subfolder_ids(folder_path):
    """
    Function to list all subfolder IDs in a given folder path
    One subfolder per patient
    Folder name should start with "sub-"
    This is used only when we load the data from the full dataset
    Does not access the fallback dataset
    """
    # Check if the given folder_path is indeed a directory
    if not os.path.isdir(folder_path):
        print(f"The provided path {folder_path} is not a directory.")
        return []

    # List all items in the given folder
    items = os.listdir(folder_path)

    # Filter out the items that are directories and match the "sub-ID" format
    subfolder_ids = []
    for item in items:
        item_path = os.path.join(folder_path, item)  # Full path to the item
        if os.path.isdir(item_path) and item.startswith(
            "sub-"
        ):  # Modify if folder structure is different
            try:
                # Extract and save the ID part
                id_part = item.split("sub-")[
                    1
                ]  # Modify if folder structure is different
                subfolder_ids.append(id_part)
            except IndexError:
                # If there's no ID part, skip this item
                continue

    return subfolder_ids


def get_image_url_for_point(row, height, width, axis_value):
    """
    Returns the image URL for a given point
    """
    return get_image_url(row["Bundle"], row["Patient_ID"], axis_value, height, width)


def calculate_image_size(num_points):
    """
    Function to calculate image size based on the number of points
    """
    max_resolution = 128  # Maximum resolution for fewer points
    min_resolution = 64  # Minimum resolution for many points
    threshold = 300  # Threshold for number of points to start decreasing resolution
    # More points -> lower resolution
    # Modify if system performance is affected

    if num_points < threshold:
        return max_resolution, max_resolution
    else:
        # Decrease resolution as number of points increases, with a square root function
        resolution = max(
            min_resolution, int(max_resolution / (num_points / threshold) ** 0.5)
        )
        return resolution, resolution
