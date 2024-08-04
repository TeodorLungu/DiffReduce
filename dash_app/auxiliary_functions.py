import io
import json

import numpy as np
import pandas as pd
from dash import no_update

import data_processing
import dim_reduction_backend
import dim_reduction_viz


def pack_params(*args):
    """
    Packs the parameters into a dictionary, used in app_integrated_data.py - update_graph() callback
    """
    return {
        "contents": args[0],
        "selection_mode": args[1],
        "begin_index": args[2],
        "end_index": args[3],
        "list_index": args[4],
        "bundle_values": args[5],
        "measure_values": args[6],
        "age_mode": args[7],
        "age_group_values": args[8],
        "begin_age": args[9],
        "end_age": args[10],
        "sex_values": args[11],
        "stratified_sampling_value": args[12],
        "stratified_sampling_value_2": args[13],
        "value_load_real_data": args[14],
        "patient_list_json": args[15],
        "modal_is_open": args[16],
        "close_button_clicks": args[17],
        "apply_button_clicks": args[18],
    }


def make_patient_list(params):
    """
    Make a list of patients based on the selection mode
    """
    # If it is a list, split the list and add the prefix
    if params["selection_mode"] == "list":
        patient_list = ["patient_" + index for index in params["list_index"].split(",")]
    # If it is a range, select the range of patients
    elif params["selection_mode"] == "range":
        # Select the range of patients based on start and end index
        begin_index_string = "patient_" + str(params["begin_index"])
        end_index_string = "patient_" + str(params["end_index"])
        patient_list = (begin_index_string, end_index_string)
    # print(patient_list)
    return patient_list


def checker_input_values(params):
    """
    Checks the parameters from the input values, in the patient selector offcanvas, and returns an error message if any of the values are missing
    Error messages are concatenated into a single string and returned
    This function also returns a boolean value indicating if there are any missing values
    """
    output = ""
    print(
        params["bundle_values"],
        params["measure_values"],
        params["age_group_values"],
        params["begin_age"],
        params["end_age"],
    )
    if not params["contents"]:
        output += "Please upload data\n"
    if not params["bundle_values"]:
        output += "Please select at least 1 bundle\n"
    if not params["measure_values"] or len(params["measure_values"]) < 2:
        output += "Please select at least 2 measures\n"
    if not params["age_group_values"] and params["age_mode"] == "age-group":
        output += "Please select an age group\n"
    if (not params["begin_age"] or not params["end_age"]) and params[
        "age_mode"
    ] == "age-range":
        output += "Please select a range of ages\n"
    if params["begin_age"] > params["end_age"]:
        output += "The beginning age should be less than the ending age\n"
    if params["begin_age"] < 0 or params["end_age"] < 0:
        output += "Age values should be positive\n"
    if not params["sex_values"]:
        output += "Please select a sex\n"
    patient_list = make_patient_list(params)
    if not patient_list:
        output += "Please select at least 1 patient\n"
    print(output)
    return output, not output == ""


def run_filters(params, all_patients_df, patient_list):
    # Make a list of patients based on the selection mode
    if params["age_mode"] == "age-group":
        age_group_list = params["age_group_values"]
        age_range = None
    elif params["age_mode"] == "age-range":
        age_group_list = None
        age_range = (params["begin_age"], params["end_age"])
    elif params["age_mode"] == "all":
        age_group_list = params["age_group_values"]
        age_range = (params["begin_age"], params["end_age"])

    # Truncate the data
    df = data_processing.truncate_data(
        patient_list,
        params["bundle_values"],
        params["measure_values"],
        age_group_list,
        age_range,
        params["sex_values"],
        all_patients_df,
    )
    return df


def run_pca(params, all_patients_df, patient_list):
    """
    Function to run PCA and return the figures and dataframes
    """
    df = run_filters(params, all_patients_df, patient_list)

    # Run PCA
    pca_df, pca, components = dim_reduction_backend.run_pca_backend(
        df, 2, normalize=True
    )

    # Run PCA for outlier detection, with different parameters (see dim_reduction_backend.py)
    pca_outlier_df, pca_outlier, components = (
        dim_reduction_backend.run_outlier_pca_backend(df)
    )

    # print(pca_df.head())
    # print(df.head())

    # Merge the PCA data with the original data, so we have all the information in one dataframe
    concatenation_list = list(params["measure_values"])
    concatenation_list.append("Patient_ID")
    merged_df = pd.merge(df[concatenation_list], pca_df, on="Patient_ID", how="inner")
    # print(merged_df.head())

    # Create the hover data
    hover_data = ["Patient", "Patient_ID", "Bundle", "Age_Group", "Age", "Sex"]
    hover_data.extend(params["measure_values"])
    # print(hover_data)

    # Create the figures

    # 2D Scatter Plot with PCA
    fig = dim_reduction_viz.create_pca_scatter_plot(
        merged_df,
        x="PC1",
        y="PC2",
        color="Bundle",
        hover_data=hover_data,
        labels={
            "PC1": "Principal Component 1",
            "PC2": "Principal Component 2",
        },
        title="2D Scatter Plot with PCA",
    )

    # PCA Loadings Line Plot
    fig_pca_loadings = dim_reduction_viz.create_loadings_line_plot(
        pca, params["measure_values"]
    )

    # Original Measures Plot Correlations and Correlation Heatmap
    fig_original_measures, fig_corr_heatmap = (
        dim_reduction_viz.create_original_measures_plot(
            df, params["measure_values"], params["stratified_sampling_value"]
        )
    )

    # PCA Explained Variance Plot, for both PCA and Outlier PCA
    fig_pca_x_variance, fig_outlier_pca_x_variance = (
        dim_reduction_viz.create_explained_variance_plot(pca, pca_outlier)
    )

    return (
        fig,
        fig_pca_loadings,
        fig_original_measures,
        fig_corr_heatmap,
        fig_pca_x_variance,
        fig_outlier_pca_x_variance,
        pca_df,
        pca_outlier_df,
        hover_data,
    )


def open_modal(params, output_checker=None, exception_message=None):
    """
    Shows the modal with the error message or output checker, if any
    Looks cleaner than having multiple return statements in the callback
    """
    if exception_message:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            not params["modal_is_open"],
            f"An error occurred while loading the scatter plot \n Usually this means that the created array through the selection, is empty \n {exception_message}",
        )
    elif output_checker:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            not params["modal_is_open"],
            output_checker,
        )
    else:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            not params["modal_is_open"],
            no_update,
        )


def get_age_group_label(age_group):
    """
    Simple function to get the age group label
    """
    labels = {1: "Infant", 2: "Development", 3: "Young Adult", 4: "Aging"}
    return labels.get(age_group, str(age_group))


def get_sex_label(sex):
    """
    Simple function to get the sex label
    """
    return "Female" if sex == 70 else "Male" if sex == 77 else str(sex)


def truncate_float(value):
    """
    Truncate floats to 4 decimal places
    """
    if isinstance(value, float):
        return np.format_float_positional(
            value, precision=4, unique=True, fractional=False
        )
    else:
        return value


def truncate_float_series(series):
    """
    Function to truncate a series of floats, using the truncate_float function
    """
    return series.apply(truncate_float)


def truncate_floats_in_df(df):
    """
    Function to apply truncate_float_series to all float columns in a DataFrame
    """
    for column in df.columns:
        if pd.api.types.is_float_dtype(df[column]):
            df[column] = truncate_float_series(df[column])
    return df


def prepare_dropdown_options(df):
    """
    Prepare the dropdown options for the bundle, measure, age, sex dropdowns, calls the helper functions if the label is not descriptive enough
    """
    bundle_options = [
        {"label": bundle, "value": bundle} for bundle in df["Bundle"].unique()
    ]
    measure_options = [
        {"label": measure, "value": measure}
        for measure in df.drop(
            ["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"], axis=1
        ).columns
    ]
    age_group_options = [
        {"label": get_age_group_label(age_group), "value": age_group}
        for age_group in df["Age_Group"].unique()
    ]
    sex_options = [
        {"label": get_sex_label(sex), "value": sex} for sex in df["Sex"].unique()
    ]

    return bundle_options, measure_options, age_group_options, sex_options


def find_key_in_nested_dict(d, target_key):
    """
    Find a key in a nested dictionary, returns the value if found, otherwise None
    This is used in the remove_plot callback to find the correct key to remove
    """
    if isinstance(d, dict):
        for key, value in d.items():
            if key == target_key:
                return value
            elif isinstance(value, dict):
                result = find_key_in_nested_dict(value, target_key)
                if result is not None:
                    return result
            elif isinstance(value, list):
                for item in value:
                    result = find_key_in_nested_dict(item, target_key)
                    if result is not None:
                        return result
    return None


def dataframes_to_json(dataframes_dict):
    """
    Dump the dataframes to JSON format
    """
    json_dict = {}
    for outer_key, inner_dict in dataframes_dict.items():
        json_dict[outer_key] = {}
        for inner_key, df in inner_dict.items():
            json_dict[outer_key][inner_key] = df.to_json(orient="split")
    return json.dumps(json_dict)


def json_to_dataframes(json_string):
    """
    Convert the JSON string to dataframes
    """
    dataframes_dict = {}
    json_dict = json.loads(json_string)
    for outer_key, inner_dict in json_dict.items():
        dataframes_dict[outer_key] = {}
        for inner_key, json_df in inner_dict.items():
            with io.StringIO(json_df) as json_buffer:
                dataframes_dict[outer_key][inner_key] = pd.read_json(
                    json_buffer, orient="split"
                )
    return dataframes_dict


def calculate_uniform_size(
    original_x_range, original_y_range, new_x_range, new_y_range, original_size
):
    """
    Used to display 2D figures in the PCA scatter plot, to maintain a uniform scaling,
    the size of the images is calculated based on the original and new ranges
    original ranges were determined empirically based on what looked good
    the result is a size that is proportional to the size of the figure
    regardless of the range of the data
    """
    # Calculate the original and new dimensions
    original_width = original_x_range[1] - original_x_range[0]
    original_height = original_y_range[1] - original_y_range[0]
    new_width = new_x_range[1] - new_x_range[0]
    new_height = new_y_range[1] - new_y_range[0]

    # Calculate the scale factors for width and height
    width_scale_factor = new_width / original_width
    height_scale_factor = new_height / original_height

    # Choose the smaller scale factor to maintain a uniform scaling
    uniform_scale_factor = min(width_scale_factor, height_scale_factor)

    # Calculate new size using the uniform scale factor
    new_size = original_size * uniform_scale_factor

    return new_size
