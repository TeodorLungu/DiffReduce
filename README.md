
# DiffReduce

  

Welcome to the repository of the DiffReduce tool. This tool has been created as part of a thesis project by Teodor Lungu, under the supervision of Professor Maxime Chamberland from Eindhoven University of Technology. The scope of the tool is to utilise PCA as a dimensionality reduction technique to visualize and analyse dMRI datasets.

  

# Detailed Installation Instructions

These instructions are for a MacOS/Linux environment

  

## Prerequisites

Before you begin, make sure you have the following installed on your system:

1. Conda - open-source package management and environment management system for Python environments. You can install it by downloading and installing Anacondra or Miniconda from their official website.

  

### Step-by-Step guide:

- Verify Conda installation

- Open a terminal (Terminal on MacOS or Linux)

- Type `conda --version` and press Enter

- If Conda is installed, you should see a version number. If not, download miniconda from the official website

- Navigate to the repository

- Use the terminal to navigate to the directory where the files I have given are located. You can use the `cd` command followed by the path to the repository. For example:

`cd your_path/Repository`

- Setup Script

- To make it easier, I have made an installation script that takes care of installing requirements and setting up an environment

- Grant permission to the setup script

-  `chmod +x setup.sh`

- Note: In general, it's good to review the contents of any Bash script before giving it execution permissions to ensure it is safe to run. You can open the script in a text editor or view it using the `cat setup.sh` command.

- Execute Setup Script

- Run the setup script by typing and running the following command in the terminal:

`./setup.sh`

- Follow the on-screen provided instructions by the script (they should appear on the terminal). The name of the environment can be chosen arbitrarily. The script will create the required Conda environment, with a name chosen by you, install the necessary packages and setup the application using `.env` varibles. The script will give an indication when it is done.

  

## Dataset Format

The tool supports datasets as .mat format. While designed to be extensible, it was specifically made for a specific dataset. As such, to use the tool as is, it is important that any dataset adheres to the following format. Nevertheless, the only thing that needs to be modified is the `data_loading.py` file in case of changes to the desired structure of the dataset.

The details about the dataset, including acquisition, sources and other details can be seen in the following paper, accessible at: [link](https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00050/118326)

```
Kurt G. Schilling, Jordan A. Chad, Maxime Chamberland, Victor Nozais, Francois Rheault, Derek Archer, Muwei Li, Yurui Gao, Leon Cai, Flavio Del’Acqua, Allen Newton, Daniel Moyer, John C. Gore, Catherine Lebel, Bennett A. Landman; White matter tract microstructure, macrostructure, and associated cortical gray matter morphology across the lifespan. __Imaging Neuroscience__ 2023; 1 1–24. doi: [https://doi.org/10.1162/imag_a_00050](https://doi.org/10.1162/imag_a_00050)
```

### Required Keys and Their Data

  

The MATLAB file must contain the following keys with their respective data types and structures:
  

#### Table Key (Default: 'X')

  

-  **Data Type:** 3D Numpy Array

-  **Shape:** (patients_count, pathways_count, features_count)

-  **Description:** This key holds the main data table with feature values for each patient and pathway.

  

#### Bundle Key (Default: 'pathways_tractseg')

  

-  **Data Type:** 2D Numpy Array

-  **Shape:** (pathways_count, 1)

-  **Description:** This key holds the names of the pathways/bundles. Each entry should be a string representing a pathway name.

  

#### ID Key (Default: 'SUBID')

  

-  **Data Type:** 1D Numpy Array

-  **Shape:** (patients_count,)

-  **Description:** This key holds the unique IDs for each patient. Each entry should be a string representing a patient's ID.

  

#### Sex Key (Default: 'SEX')

  

-  **Data Type:** 1D Numpy Array

-  **Shape:** (patients_count,)

-  **Description:** This key holds the sex of each patient. Each entry should be an integer (e.g., 0 for female, 1 for male).

  

#### Age Key (Default: 'AGE')

 
-  **Data Type:** 1D Numpy Array

-  **Shape:** (patients_count,)

-  **Description:** This key holds the age of each patient. Each entry should be a float/integer representing the patient's age.

  

#### Age Group Key (Default: 'DATASET')

-  **Data Type:** 1D Numpy Array

-  **Shape:** (patients_count,)

-  **Description:** This key holds the age group of each patient. Each entry should be an integer representing the patient's age group (In this specific case there are 4 age groups)

  

#### Example Structure of a MATLAB File

  

Matlab File Structure:

  

```python

{

'X': np.array([[[...], [...], ...]]), # Shape: (patients_count, pathways_count, features_count)

'pathways_tractseg': np.array([['bundle1'], ['bundle2'], ...]), # Shape: (pathways_count, 1)

'SUBID': np.array(['ID1', 'ID2', ...]), # Shape: (patients_count,)

'SEX': np.array([[0], [1], ...]), # Shape: (patients_count,)

'AGE': np.array([[25.0], [30.5], ...]), # Shape: (patients_count,)

'DATASET': np.array([[1], [2], ...]) # Shape: (patients_count,)

}

```

The resulting Python formatted dataset looks as follows:

| Patient | Patient\_ID | Age\_Group    | Sex  | Age  | Bundle   | FA    | MD    | AD    | $\dots$ | Volume    |
|---------|-------------|---------------|------|------|----------|-------|-------|-------|---------|-----------|
| $P_1$   | $PID_1$     | $Age\_Group_1$| $Sex_1$ | $Age_1$ | $Bundle_1$  | $FA_1^1$  | $MD_1^1$  | $AD_1^1$  | $\dots$ | $Volume_1^1$  |
| $P_1$   | $PID_1$     | $Age\_Group_1$| $Sex_1$ | $Age_1$ | $Bundle_2$  | $FA_1^2$  | $MD_1^2$  | $AD_1^2$  | $\dots$ | $Volume_1^2$  |
| $\vdots$| $\vdots$    | $\vdots$      | $\vdots$ | $\vdots$ | $\vdots$    | $\vdots$ | $\vdots$ | $\vdots$ | $\dots$ | $\vdots$      |
| $P_2$   | $PID_2$     | $Age\_Group_2$| $Sex_2$ | $Age_2$ | $Bundle_1$  | $FA_2^1$  | $MD_2^1$  | $AD_2^1$  |         | $Volume_2^1$  |
| $\vdots$| $\vdots$    | $\vdots$      | $\vdots$ | $\vdots$ | $\vdots$    | $\vdots$ | $\vdots$ | $\vdots$ | $\dots$ | $\vdots$      |
| $P_n$   | $PID_n$     | $Age\_Group_n$| $Sex_n$ | $Age_n$ | $Bundle_{72}$ | $FA_n^{72}$ | $MD_n^{72}$ | $AD_n^{72}$ |         | $Volume_n^{72}$ |

  The dataset should also include FA maps, and .tck streamline files, based on [TractSeg](https://www.sciencedirect.com/science/article/pii/S1053811918306864). The structure of this type of data is as follows:
```
Data
└── Patients
├── sub-*
│ ├── TOM_trackings
│ │ └── *.tck files
│ └── dti__FA.nii.gz
```

## Setup Instructions - The Dataset

To setup the location of the .tck files, screenshots for 2D visualization and FA map for proper usage of the application, I use environment variables, that must be changed to the correct paths in the `.env` file. Follow the two steps below on how to do this.

  

A `.env` file is used to store environment variables, such that they can be accessed by the application to configure user-specific settings such as file paths. This file will containt the variables needed for locating two folders needed for the application.

  

- Locate the `.env` file

- After the setup script completes, locate the `.env` file in the directory `Repository/dash_app/.env`.

Note: Files that start with a dot (.) are hidden by default. You can view them using `Command + Shift + .` (period) to toggle the visibility on MacOS or `Ctrl + H` on Linux operating systems. Alternatively, opening the whole project in VSCode will by default show such files.

- Edit the `.env` file

- Open the `.env` file using a text editor of your choice (TextEdit, nano, VSCode)

- You will see two environment variables `BASE_DIR_FULL` and `BASE_DIR_FALLBACK`.

- The full directory should contain all the available data

- The fallback directory should contain a single scan, with the below structure for falling back to in case the tck data or screenshots are not available

- Set these variables to the absolute paths of the corresponding directories on your host machine

- Note the " " for the folders

`

BASE_DIR_FULL="/your_path/Data/Full_Data/Patients"

BASE_DIR_FALLBACK="/your_path/Data/FallBack_Data/Patients"

`

- The data directories need to match the following structures

```

Full_Data

└── Patients

├── sub-*

│ ├── Screenshots

│ │ └── *.png files

│ ├── TOM_trackings

│ │ └── *.tck files

│ └── dti__FA.nii.gz

```

and

```

FallBack_Data

└── Patients

├── Patient_0

│ ├── Screenshots

│ │ └── *.png files

│ ├── TOM_trackings

│ │ └── *.tck files

│ └── 100206__fa.nii.gz

```

- If needed, you can modify the folder structure and the corresponding `image_backend` to fit your specific needs. This structure is based on the output from TractSeg and the Screenshot script.

  

## Run Instructions

- Activate the Conda Environment

- Open a terminal and activate the Conda environment created by the setup script. Replace `<name>` with the actual name of the environment.

`conda activate <name>`

  

- Run the Dash Application

- Navigate to the `dash_app` directory within the repository, using the terminal:

`cd dash_app`

Run the application using Python

`python app_integrated_data.py`

  

- Access the Dash Application

- Open a web browser and go to the following URL:

`http://localhost:8051`

- You should see the Dash application interface.

- If you encounter a `Error loading layout`, close and restart the Python application and reload the page. You can use the same command - `python app_integrated_data.py`

## Maintenance Instructions

  

- Managing File System Caches

- The application uses two distinct file system caches located in the `cache` and `file_system_backend` folders.

- Periodically empty these folders to free up storage space. Make sure the application is not running when you do this to avoid any issues.

  

## Screenshot script instructions

  

- This is how to use the scripts to generate the screenshots required for the application. This script uses asynchronous functions (will most likely max out the available RAM memory and CPU).

  

- There are two files in the screenshots folder.

- The first one `Repository/ScreenshotsScripts/modified_ss_script_adjusted.py` is a modification of a Scilpy script (https://scilpy.readthedocs.io/en/latest/scripts/scil_viz_bundle_screenshot_mosaic.html), to handle the outputting of 6 distinct axis views as .png files (axial superior, axial inferior, etc.) in 6 different files for each of the given .vtk file. That is, for `AF_left.tck`, we will have the following 6 files:

  

```

AF_left_axial_inferior.png

AF_left_axial_superior.png

AF_left_coronal_anterior.png

AF_left_coronal_posterior.png

AF_left_sagittal_left.png

AF_left_sagittal_right.png

```

- The second file `Repository/ScreenshotsScripts/script_run_ss_concurrent.py` is a new file made for running the previous script asynchronously, due to speed considerations. The tasks are not intensive, but they require parallelism to handle processing 72 bundles simultaneously per patient. The processing of 1 patient takes around 30 seconds.

- This script contains a variable `SCRIPT_PATH`. Please enter the absolute path of the `modified_ss_script_adjusted.py` file here, as a string.

- To run this script use `python modifed_ss_script_adjusted.py` in the terminal and enter the base path for the folder containing the patient that requires the generation of screenshots when prompted in the terminal. The folder structure was given previously. So for example, the path would be `/your_path/Full_Data/Patients`. This will automatically detect all patients, and run the script without manual intervention, provided the structure is identical to what I provided. Alternatively, the script can be adjusted to handle a different structure.
