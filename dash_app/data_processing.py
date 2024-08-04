import pandas as pd


def extract_patients_in_range(df, patient_range_begin, patient_range_end):
    """
    Extracts the list of unique patients within a specified range from a DataFrame.

    Parameters:
    - df (DataFrame): The DataFrame containing the patient data.
    - patient_range_begin (str): The beginning of the patient range.
    - patient_range_end (str): The end of the patient range.

    Returns:
    - patients_in_range (list): List of unique patients within the specified range.
    """
    # Extract the numeric part from the 'Patient' column and convert it to numeric
    df["Patient_Num"] = pd.to_numeric(df["Patient"].str.extract("(\d+)")[0])

    # Create a list of unique patients in the specified range
    patients_in_range = (
        df.loc[
            (df["Patient_Num"] >= int(patient_range_begin.split("_")[1]))
            & (df["Patient_Num"] <= int(patient_range_end.split("_")[1])),
            "Patient",
        ]
        .unique()
        .tolist()
    )

    # Display the resulting list
    return patients_in_range


def truncate_data_backend(
    dataframe,
    bundle_list,
    patient_list,
    measure_list,
    age_group_list,
    age_group_range,
    sex_list,
):
    """
    Truncates the DataFrame based on specified patient, bundle, and measure lists, and age, sex, age_group ranges.

    Parameters:
    - dataframe (DataFrame): The original DataFrame containing the data.
    - bundle_list (list): List of bundles to include in the truncated DataFrame.
    - patient_list (list): List of patients to include in the truncated DataFrame.
    - measure_list (list): List of measures to include in the truncated DataFrame.
    - age_group_list (list): List of age groups to include in the truncated DataFrame.
    - age_group_range (tuple): Tuple representing the age range.
    - sex_list (list): List of sexes to include in the truncated DataFrame.
    - dataframe (DataFrame): The original DataFrame containing the data.

    Returns:
    - filtered_df (DataFrame): Truncated DataFrame based on the specified lists.
    """
    if age_group_list is not None and age_group_range is not None:
        # print("Both age_group_list and age_group_range are specified.")
        filtered_df = dataframe[
            (dataframe["Patient"].isin(patient_list))
            & (dataframe["Bundle"].isin(bundle_list))
            & (dataframe["Age_Group"].isin(age_group_list))
            & (dataframe["Age"] >= age_group_range[0])
            & (dataframe["Age"] <= age_group_range[1])
            & (dataframe["Sex"].isin(sex_list))
        ]
    elif age_group_list is not None:
        # print("Only age_group_list is specified.")
        filtered_df = dataframe[
            (dataframe["Patient"].isin(patient_list))
            & (dataframe["Bundle"].isin(bundle_list))
            & (dataframe["Age_Group"].isin(age_group_list))
            & (dataframe["Sex"].isin(sex_list))
        ]
    elif age_group_range is not None:
        # print("Only age_group_range is specified.")
        filtered_df = dataframe[
            (dataframe["Patient"].isin(patient_list))
            & (dataframe["Bundle"].isin(bundle_list))
            & (dataframe["Age"] >= age_group_range[0])
            & (dataframe["Age"] <= age_group_range[1])
            & (dataframe["Sex"].isin(sex_list))
        ]
    filtered_df = filtered_df[
        ["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"] + measure_list
    ]
    filtered_df.reset_index(inplace=True, drop=True)
    return filtered_df


def truncate_data(
    patient_list,
    bundle_list,
    measure_list,
    age_group_list,
    age_group_range,
    sex_list,
    dataframe,
):
    """
    Truncate data based on specified patient, bundle, and measure lists from a DataFrame.

    Parameters:
    - patient_list (list or tuple): List of patients or tuple representing a range.
    - bundle_list (list): List of bundles to include in the truncated DataFrame.
    - measure_list (list): List of measures to include in the truncated DataFrame.
    - age_group_list (list): List of age groups to include in the truncated DataFrame.
    - age_group_range (tuple): Tuple representing the age range.
    - sex_list (list): List of sexes to include in the truncated DataFrame.
    - dataframe (DataFrame): The original DataFrame containing the data.

    Returns:
    - filtered_df (DataFrame): Truncated DataFrame based on the specified lists.
    """
    if isinstance(patient_list, list):
        # If patient_list is a list
        filtered_df = truncate_data_backend(
            dataframe,
            bundle_list,
            patient_list,
            measure_list,
            age_group_list,
            age_group_range,
            sex_list,
        )
    elif isinstance(patient_list, tuple) and len(patient_list) == 2:
        # If patient_list is a tuple representing a range
        patient_range_begin, patient_range_end = patient_list
        patient_list = extract_patients_in_range(
            dataframe, patient_range_begin, patient_range_end
        )
        filtered_df = truncate_data_backend(
            dataframe,
            bundle_list,
            patient_list,
            measure_list,
            age_group_list,
            age_group_range,
            sex_list,
        )
    else:
        # Handle other cases or raise an exception
        raise ValueError("Invalid patient_list format")

    return filtered_df
