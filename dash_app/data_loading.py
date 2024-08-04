import base64
import io

import numpy as np
import pandas as pd
import scipy.io


def extract_string_from_object(obj):
    """
    Extract a string from an object, recursively
    """
    # Check if the object is a string
    if isinstance(obj, str):  # If it is a string, return it
        return obj
    # Check if the object is a list, tuple, or numpy array and has at least one element
    elif isinstance(obj, (list, tuple, np.ndarray)) and len(obj) > 0:
        # Recursively extract from the first element
        return extract_string_from_object(obj[0])
    # Check if the object is null
    elif pd.isnull(obj):
        return None  # no need to convert
    return str(obj)  # Convert to string


def load_data(
    contents,
    table_key="X",
    bundle_key="pathways_tractseg",
    id_key="SUBID",
    sex_key="SEX",
    age_key="AGE",
    age_group_key="DATASET",
):
    """
    Load data from a MATLAB file
    Based on the contents of the file, extract the table data, bundle names, and ID names, Sex, Age, Age Group.
    """
    try:
        # Split the contents into _ and content_string
        _, content_string = contents.split(",")

        # Decode the base64 string
        decoded = base64.b64decode(content_string)

        # Read the decoded contents using io.BytesIO
        mat_data = scipy.io.loadmat(io.BytesIO(decoded))

        # Access the table data
        table_data = mat_data.get(table_key)

        # Access the bundle names
        pathways_tractseg = mat_data.get(bundle_key)

        # Access the sex
        sex_data = mat_data.get(sex_key)

        # Access the age
        age_data = mat_data.get(age_key)

        # Access the age group
        age_group_data = mat_data.get(age_group_key)

        # Access the ID names
        id_data = mat_data.get(id_key)

        # Check if the keys are present in the MATLAB file
        if (
            table_data is None
            or pathways_tractseg is None
            or id_data is None
            or sex_data is None
            or age_data is None
            or age_group_data is None
        ):
            raise ValueError(
                f"Keys '{table_key}' or '{bundle_key}' or '{id_key}' or '{sex_key}' or '{age_key}' or '{age_group_key}' not found in the MATLAB file."
            )

        # Return all tables
        return (
            table_data,
            pathways_tractseg,
            id_data,
            sex_data,
            age_data,
            age_group_data,
        )

    except Exception as e:
        raise Exception(f"An error occurred while loading the MATLAB file: {e}")


def transform_mat_to_df(
    table_data,
    pathways_tractseg,
    id_data,
    sex_data,
    age_data,
    age_group_data,
    index_names=None,
):
    """
    Transform MATLAB data to a pandas DataFrame.
    """
    try:
        # Rename the dimensions
        patients_count, pathways_count, features_count = table_data.shape
        if len(pathways_tractseg) != pathways_count:
            raise ValueError(
                "Mismatch in pathways count between table_data and pathways_tractseg."
            )

        # Create patient names
        patient_names = [f"patient_{i}" for i in range(patients_count)]

        # Extract column names from the nested arrays
        column_names = [pathways_tractseg[i][0][0] for i in range(pathways_count)]

        # Set default index names if not provided
        if index_names is None:
            index_names = [
                "FA",
                "MD",
                "AD",
                "RD",
                "ICVF",
                "ISOVF",
                "OD",
                "wm_volume",
                "volume_endpoints",
                "streamlines_count",
                "avg_length",
                "std_length",
                "min_length",
                "max_length",
                "span",
                "curl",
                "diameter",
                "elongation",
                "surface_area",
                "end_surface_area_head",
                "end_surface_area_tail",
                "radius_head",
                "radius_tail",
                "irregularity",
                "irregularity_of_end_surface_head",
                "irregularity_of_end_surface_tail",
                "mean_curvature",
                "fractal_dimension",
                "area",
                "curv",
                "jacobian_white",
                "sulc",
                "thickness",
                "volume",
            ]

        # Initialize an empty list to store DataFrames for each patient
        dfs = []

        # Iterate over patients
        for i in range(patients_count):
            patient_data = table_data[
                i, :, :
            ].T  # Transpose to match the column indices
            df_patient = pd.DataFrame(
                patient_data.T, columns=index_names, index=column_names
            )
            extracted_string = extract_string_from_object(
                id_data[i]
            )  # Extract the string from the object
            # Add a new column for unique patient ID
            df_patient["Patient_ID"] = [extracted_string] * len(df_patient)
            # Add new columns for sex, age, and age group, if available
            df_patient["Sex"] = int(sex_data[i][0]) if sex_data[i].size else np.nan
            df_patient["Age"] = float(age_data[i][0]) if age_data[i].size else np.nan
            df_patient["Age_Group"] = (
                int(age_group_data[i][0]) if age_group_data[i].size else np.nan
            )
            # Append the DataFrame to the list
            dfs.append(df_patient)

        # Concatenate the list of DataFrames into a single DataFrame
        df = pd.concat(dfs, keys=patient_names, names=["Patient", "Bundle"])
        df = df.reset_index()

        # Now, df is a pandas DataFrame with proper row and column names
        return df
    except Exception as e:
        raise Exception(
            f"An error occurred while transforming MATLAB data to DataFrame: {e}"
        )
