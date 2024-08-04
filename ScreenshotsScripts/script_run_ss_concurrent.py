import asyncio
import os
import time
import tracemalloc
from asyncio import subprocess

"""
DO NOT FORGET TO ADJUST COMMAND PATHS
"""
SCRIPT_PATH = "/Users/teodorlungu/Documents/GitHub/dMRI-Thesis-2023/ScreenshotsScripts/modified_ss_script_adjusted.py"


async def find_files(directory, extension):
    """
    Find all files with a specific extension in a given directory and its subdirectories.

    Args:
        directory (str): The directory to search for files.
        extension (str): The file extension to filter the search.

    Returns:
        list: A list of file paths that match the given extension.
    """
    result = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                result.append(os.path.join(root, file))
    return result


async def find_nii_gz_file(directory):
    """
    Finds the first .nii.gz file in the specified directory or its subdirectories.

    Args:
        directory (str): The directory to search for the .nii.gz file.

    Returns:
        str: The path of the first .nii.gz file found.

    Raises:
        FileNotFoundError: If no .nii.gz file is found in the directory or its subdirectories.
    """
    try:
        files = await find_files(directory, ".nii.gz")
        return files[0]
    except IndexError:
        raise FileNotFoundError(
            "No .nii.gz file found in the directory or its subdirectories."
        )


async def visualize_single_bundle(
    patient_directory, reference_path, input_volume_path, tck_file, semaphore
):
    """
    Visualizes a single bundle using the modified_ss_script_adjusted.py script.

    Args:
        patient_directory (str): The directory path of the patient.
        reference_path (str): The path to the reference file.
        input_volume_path (str): The path to the input volume file.
        tck_file (str): The path to the tck file.
        semaphore (asyncio.Semaphore): A semaphore to limit the number of concurrent executions.

    Returns:
        bool: True everytime (do not raise errors, just log them to error.log)
    """
    output_folder = os.path.join(patient_directory, "Screenshots")
    os.makedirs(output_folder, exist_ok=True)

    output_file = f"{os.path.splitext(os.path.basename(tck_file))[0]}.png"
    full_output_path = os.path.join(output_folder, output_file)

    command = [
        "python",
        SCRIPT_PATH,
        "--all_different_files",
        "--no_information",
        "--no_bundle_name",
        "--no_streamline_number",
        "--reference",
        reference_path,
        input_volume_path,
        tck_file,
        full_output_path,
    ]

    async with semaphore:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False
        )
        out, err = await process.communicate()

        if err:
            with open("error.log", "a") as error_file:
                error_file.write(err.decode("UTF-8"))

    return True


async def run_visualize_bundles_for_all_patients(base_directory, max_workers=None):
    """
    Runs the visualization of bundles for all patients in the given base directory.

    Args:
        base_directory (str): The base directory containing patient directories.
        max_workers (int, optional): The maximum number of workers to use for concurrent processing. Defaults to None.

    Returns:
        None
    """
    start_total_time = time.time()

    patient_directories = [
        os.path.join(base_directory, patient_dir)
        for patient_dir in next(os.walk(base_directory))[1]
    ]
    reference_paths = [
        await find_nii_gz_file(patient_directory)
        for patient_directory in patient_directories
    ]
    print("Processing Patients")
    print("The number of patients is: %f", len(patient_directories))

    semaphore = asyncio.Semaphore(max_workers)

    tasks = []
    for patient_directory, reference_path in zip(patient_directories, reference_paths):
        tck_files = await find_files(patient_directory, ".tck")
        for tck_file in tck_files:
            task = visualize_single_bundle(
                patient_directory, reference_path, reference_path, tck_file, semaphore
            )
            tasks.append(task)
    print(len(tasks))
    await asyncio.gather(*tasks)

    end_total_time = time.time()
    total_time = end_total_time - start_total_time
    print(f"Total time taken: {total_time} seconds")


if __name__ == "__main__":
    tracemalloc.start()

    base_directory = input("Enter the base directory path containing patient folders: ")
    asyncio.run(run_visualize_bundles_for_all_patients(base_directory, max_workers=50))

    tracemalloc.stop()
