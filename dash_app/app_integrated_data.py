import datetime
import io
import random
import re

import dash_bootstrap_components as dbc
import diskcache
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import (
    ALL,
    MATCH,
    DiskcacheManager,
    Input,
    Output,
    Patch,
    State,
    callback,
    callback_context,
    dcc,
    html,
)
from dash_extensions.enrich import (
    DashProxy,
    Serverside,
    ServersideOutputTransform,
    no_update,
)
from flask import send_file

import auxiliary_functions
import data_loading
import dim_reduction_viz
import image_backend
import outlier_detection
import principal_components_age_corr_regression_viz
import tck_file_loading
from constants import (
    DBC_CSS,
    DBC_THEME,
    DEFAULT_AGE_GROUPS,
    DEFAULT_BUNDLES,
    DEFAULT_MEASURES,
    DEFAULT_SEXES,
    IMAGE_DOWNLOAD_OPTIONS,
)
from content_layout import content_layout

# Cache Managers
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

# App Setup
app = DashProxy(
    external_stylesheets=[DBC_THEME, DBC_CSS],
    transforms=[ServersideOutputTransform()],
    background_callback_manager=background_callback_manager,
)

# Placeholder for the scatter plot figure
fig = px.scatter()
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)


# App layout
# Includes definitions for html components, dash components and any other layout elements
app.layout = content_layout.create_content_layout()


@app.callback(
    [
        Output("bundle-dropdown", "options"),
        Output("measure-dropdown", "options"),
        Output("age-group-dropdown", "options"),
        Output("sex-dropdown", "options"),
        Output("patient-list-store", "data"),
        # This is for default values for faster prototyping
        # Start Deltion in prod
        Output("bundle-dropdown", "value"),
        Output("measure-dropdown", "value"),
        Output("age-group-dropdown", "value"),
        Output("sex-dropdown", "value"),
        # End Deletion in prod
    ],
    [Input("upload-data", "contents")],
)
def update_dropdown_options(contents):
    """
    Updates the dropdown options based on the uploaded data (runs only once every time data is uploaded)
    """
    if contents is None:
        return [no_update] * 9

    try:
        table_data, pathways_tractseg, id_data, sex_data, age_data, age_group_data = (
            data_loading.load_data(contents)
        )
        df = data_loading.transform_mat_to_df(
            table_data, pathways_tractseg, id_data, sex_data, age_data, age_group_data
        )
        options = auxiliary_functions.prepare_dropdown_options(df)
        return [
            *options,
            Serverside(df),
            DEFAULT_BUNDLES,
            DEFAULT_MEASURES,
            DEFAULT_AGE_GROUPS,
            DEFAULT_SEXES,
        ]
    except Exception as e:
        raise Exception(f"Failed to load or process data: {e}")


@app.callback(
    [
        Output("load-images-switch", "value"),
        Output("graph-2-dcc", "relayoutData", allow_duplicate=True),
    ],
    [
        Input("pca-data-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_load_images_switch(data):
    """
    Callback to reset the load images switch and the relayout data of the scatter plot upon a change of the PCA data
    """
    return [False, {"xaxis.autorange": True, "yaxis.autorange": True}]


@app.callback(
    [
        Output("graph-2-dcc", "figure", allow_duplicate=True),
        Output("added-points-store", "data"),
        Output("load-images-switch-prev", "data"),
    ],
    [
        State("pca-data-store", "data"),
        State("added-points-store", "data"),
        Input("graph-2-dcc", "relayoutData"),
        Input("load-images-switch", "value"),
        State("graph-2-dcc", "figure"),
        Input("image-view-axis-dropdown", "value"),
        State("original-plot-x-y-axis", "data"),
        State("load-images-switch-prev", "data"),
    ],
    prevent_initial_call=True,
    background=True,
    running=[
        (
            Output("image_loading_container", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
)
def update_graph_based_on_images(
    pca_df_test_2,
    points_that_were_added,
    relayoutData,
    load_images_switch_value,
    figure,
    axis_value,
    x_y_original_values_json,
    prev_load_images_switch_value,
):
    tic_total = datetime.datetime.now()
    """
    Manages the update of the scatter plot based on images projected directly to the 2D PCA plot
    """

    # Checks if the trigger is the graph or the button
    # Gets callback context
    ctx = callback_context

    # Checks if it has not been triggered
    if not ctx.triggered:
        return no_update, no_update

    if ctx.triggered_id == "graph-2-dcc" or ctx.triggered_id == "load-images-switch":
        # print(relayoutData)
        # If previous state was not changed, then do nothing
        # Avoids unnecessary checks
        if load_images_switch_value != prev_load_images_switch_value:
            # Check if load_images_switch_value is True
            if load_images_switch_value:
                # Checks if the relayoutData is not None
                if relayoutData:
                    fig = go.Figure(figure)

                    # Determine x and y ranges
                    if (
                        "xaxis.range[0]" in relayoutData
                        or "yaxis.range[0]" in relayoutData
                    ):
                        x_range = [
                            relayoutData.get(
                                "xaxis.range[0]", figure["layout"]["xaxis"]["range"][0]
                            ),
                            relayoutData.get(
                                "xaxis.range[1]", figure["layout"]["xaxis"]["range"][1]
                            ),
                        ]
                        y_range = [
                            relayoutData.get(
                                "yaxis.range[0]", figure["layout"]["yaxis"]["range"][0]
                            ),
                            relayoutData.get(
                                "yaxis.range[1]", figure["layout"]["yaxis"]["range"][1]
                            ),
                        ]

                    # If autosize or autorange is in relayoutData (reset button was clicked)
                    elif (
                        "autosize" in relayoutData
                        or "xaxis.autorange" in relayoutData
                        or "yaxis.autorange" in relayoutData
                    ):
                        # Get the original x and y ranges
                        x_range = fig.full_figure_for_development().layout.xaxis.range
                        y_range = fig.full_figure_for_development().layout.yaxis.range
                    else:
                        return no_update, no_update

                    # print(x_range, y_range)

                    # Create the figure
                    fig.update_layout(
                        xaxis=dict(range=x_range), yaxis=dict(range=y_range)
                    )

                    # Filter visible points
                    visible_points = pca_df_test_2.query(
                        "PC1 >= @x_range[0] and PC1 <= @x_range[1] and PC2 >= @y_range[0] and PC2 <= @y_range[1]"
                    )

                    if points_that_were_added is not None:
                        points_that_were_added = points_that_were_added
                    else:
                        points_that_were_added = pd.DataFrame()

                    # Compute points to be added and deleted
                    current_points_set = set(
                        visible_points.apply(
                            lambda row: (
                                row["Patient"],
                                row["Patient_ID"],
                                row["Bundle"],
                            ),
                            axis=1,
                        )
                    )
                    previous_points_set = set(
                        points_that_were_added.apply(
                            lambda row: (
                                row["Patient"],
                                row["Patient_ID"],
                                row["Bundle"],
                            ),
                            axis=1,
                        )
                    )

                    # Only add points that are not already in the figure
                    points_to_add = current_points_set - previous_points_set
                    # Only delete points that are not in the current set
                    points_to_delete = previous_points_set - current_points_set

                    # Update global variable
                    points_that_were_added = visible_points

                    # Calculate image size based on the number of points that will are visible
                    image_width, image_height = image_backend.calculate_image_size(
                        len(visible_points)
                    )
                    # print(image_height, image_width)

                    tic_get_image_urls = datetime.datetime.now()
                    # Define a function to process each point
                    image_urls_dict = {
                        point: image_backend.get_image_url_for_point(
                            visible_points[
                                (visible_points["Patient"] == point[0])
                                & (visible_points["Patient_ID"] == point[1])
                                & (visible_points["Bundle"] == point[2])
                            ].iloc[0],
                            image_width,
                            image_height,
                            axis_value,
                        )
                        for point in points_to_add
                    }
                    toc_get_image_urls = datetime.datetime.now()
                    print(
                        "Time to get image URLs:",
                        toc_get_image_urls - tic_get_image_urls,
                    )

                    # Match rows based on conditions
                    matching_rows = visible_points[
                        visible_points.set_index(
                            ["Patient", "Patient_ID", "Bundle"]
                        ).index.isin(points_to_add)
                    ]
                    existing_images = figure["layout"].get("images", [])
                    x_y_original_values = x_y_original_values_json[0]
                    new_size = auxiliary_functions.calculate_uniform_size(
                        [0, 5],
                        [0, 7],
                        x_y_original_values[0],
                        x_y_original_values[1],
                        0.8,
                    )
                    # print(new_size)

                    # Create Image objects with image URLs
                    images_to_add = [
                        go.layout.Image(
                            name=str(row["Patient"])
                            + "_"
                            + str(row["Patient_ID"])
                            + "_"
                            + str(row["Bundle"]),
                            source=image_urls_dict.get(
                                (
                                    str(row["Patient"]),
                                    str(row["Patient_ID"]),
                                    str(row["Bundle"]),
                                ),
                                None,
                            ),
                            xref="x",
                            yref="y",
                            xanchor="center",
                            yanchor="middle",
                            x=row["PC1"],
                            y=row["PC2"],
                            sizex=float(new_size),
                            sizey=float(new_size),
                            sizing="contain",
                            opacity=0.8,
                            layer="above",
                            visible=True,
                        )
                        for _, row in matching_rows.iterrows()
                    ]
                    updated_images = existing_images + images_to_add
                    print(
                        "Time to create image objects:",
                        datetime.datetime.now() - toc_get_image_urls,
                    )

                    # Update the figure with the images calculated previously
                    fig.update_layout(images=updated_images)

                    toc_add_pictures = datetime.datetime.now()
                    print("Time to add pictures:", toc_add_pictures - tic_total)
                    # print(fig.layout.images)

                    # Delete images that are up for deletion (not visible)
                    names_to_delete = {
                        str(point[0]) + "_" + str(point[1]) + "_" + str(point[2])
                        for point in points_to_delete
                    }
                    for img in fig.layout.images:
                        if img["name"] in names_to_delete:
                            # print("Deleting image")
                            img["visible"] = False

                    return (
                        fig,
                        Serverside(points_that_were_added),
                        load_images_switch_value,
                    )
            # If load_images_switch_value is False, then delete all images
            else:
                fig = go.Figure(figure)
                fig.update_layout_images(visible=False)

                toc_no_pictures = datetime.datetime.now()
                print("Time to not add pictures:", toc_no_pictures - tic_total)

                return [fig, None, load_images_switch_value]
        # If the switch was not changed, then return the previous state
        else:
            return [no_update, no_update, load_images_switch_value]
    else:
        return [no_update, no_update, prev_load_images_switch_value]


@app.callback(
    [
        Output("graph-2-dcc", "figure", allow_duplicate=True),
        Output("graph-pca-loadings", "figure", allow_duplicate=True),
        Output("graph-original-measures", "figure", allow_duplicate=True),
        Output("graph-correlation-heatmap", "figure", allow_duplicate=True),
        Output("graph-explained-variance", "figure"),
        Output("graph-explained-outlier-variance", "figure"),
        Output("scatter-plot-bundle-dropdown", "options"),
        Output("original-measures-dropdown", "options"),
        Output("pca-data-store", "data"),
        Output("pca-outlier-store", "data"),
        Output("hover-data-store", "data"),
        Output("modal_patient_selector_error", "is_open"),
        Output("modal_patient_selector_error_body", "children"),
    ],
    [
        State("upload-data", "contents"),
        State("selection-mode", "value"),
        State("begin-index", "value"),
        State("end-index", "value"),
        State("list-index", "value"),
        State("bundle-dropdown", "value"),
        State("measure-dropdown", "value"),
        State("age-mode", "value"),
        State("age-group-dropdown", "value"),
        State("begin-age", "value"),
        State("end-age", "value"),
        State("sex-dropdown", "value"),
        State("input-stratified-sampling", "value"),
        State("input-stratified-sampling-2", "value"),
        State("load-real-data-selector", "value"),
        State("patient-list-store", "data"),
        State("modal_patient_selector_error", "is_open"),
        Input("modal_patient_selector_close", "n_clicks"),
        Input("apply-changes-button", "n_clicks"),
        State("original-measures-dropdown", "value"),
        Input("change-splom-button", "n_clicks"),
    ],
    prevent_initial_call=True,
    running=[
        (Output("apply-changes-button", "disabled"), True, False),
        (Output("change-splom-button", "disabled"), True, False),
    ],
    background=True,
)
def update_graph(
    upload_contents,
    selection_mode,
    begin_index,
    end_index,
    list_index,
    bundle_value,
    measure_value,
    age_mode,
    age_group_value,
    begin_age,
    end_age,
    sex_value,
    stratified_sampling_value,
    stratified_sampling_value_2,
    value_load_real_data,
    all_patients_df,
    modal_is_open,
    modal_close_clicks,
    apply_changes_clicks,
    original_measures_value,
    change_splom_clicks,
):
    """
    Main callback function to update the PCA scatter plot and related plots
    """
    # For easier handling during invocation of other functions, this is used to pack all the parameters
    params = auxiliary_functions.pack_params(
        upload_contents,
        selection_mode,
        begin_index,
        end_index,
        list_index,
        bundle_value,
        measure_value,
        age_mode,
        age_group_value,
        begin_age,
        end_age,
        sex_value,
        stratified_sampling_value,
        stratified_sampling_value_2,
        value_load_real_data,
        all_patients_df,
        modal_is_open,
        modal_close_clicks,
        apply_changes_clicks,
    )
    # Gets callback context
    ctx = callback_context

    # Checks if it has not been triggered
    if not ctx.triggered:
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
            no_update,
            no_update,
            no_update,
        )

    # Check if the button for closing the modal was clicked
    if ctx.triggered_id == "modal_patient_selector_close":
        return auxiliary_functions.open_modal(params)

    # Check if the button for applying changes was clicked
    if ctx.triggered_id == "apply-changes-button" or "change-splom-button":
        # Check if the contents, bundle_values, and measure_values are not None
        output_checker, output_checker_bool = auxiliary_functions.checker_input_values(
            params
        )
        # Check the parameters and return the modal if there is an error
        if output_checker_bool:
            return auxiliary_functions.open_modal(params, output_checker=output_checker)

        # Check if the button for loading real data was clicked
        if params["value_load_real_data"]:
            try:
                # Get the list of patients with real data
                patient_list = image_backend.list_subfolder_ids(
                    image_backend.BASE_DIR_FULL
                )
                # Filter the DataFrame
                filtered_df = all_patients_df[
                    all_patients_df["Patient_ID"].isin(patient_list)
                ]
                patient_list = filtered_df["Patient"].tolist()
            except Exception as e:
                return auxiliary_functions.open_modal(params, exception_message=e)
                # raise Exception(f"An error occurred while loading the scatter plot {e}")
        else:
            try:
                patient_list = auxiliary_functions.make_patient_list(params)
            except Exception as e:
                return auxiliary_functions.open_modal(params, exception_message=e)
                # raise Exception(f"An error occurred while loading the scatter plot {e}")
        if ctx.triggered_id == "change-splom-button":
            dataframe_filtered_splom = auxiliary_functions.run_filters(
                params, all_patients_df, patient_list
            )
            if isinstance(original_measures_value, str):
                filter = [original_measures_value, "Bundle"]
                original_measures_value = [original_measures_value]
            elif isinstance(original_measures_value, list) and all(
                isinstance(item, str) for item in original_measures_value
            ):
                filter = original_measures_value + ["Bundle"]
            if filter != ["Bundle"]:
                dataframe_filtered_splom = dataframe_filtered_splom[filter]
            else:
                original_measures_value = params["measure_values"]
            fig_splom, _ = dim_reduction_viz.create_original_measures_plot(
                dataframe_filtered_splom,
                original_measures_value,
                params["stratified_sampling_value_2"],
            )
            return (
                no_update,
                no_update,
                fig_splom,
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
            )
        try:
            # Run PCA and related plots
            (
                fig,
                fig_pca_loadings,
                fig_original_measures,
                fig_corr_heatmap,
                fig_pca_x_variance,
                fig_outlier_pca_x_variance,
                pca_df,
                pca_outlier_df,
                hover_data,
            ) = auxiliary_functions.run_pca(params, all_patients_df, patient_list)
            return (
                fig,
                fig_pca_loadings,
                fig_original_measures,
                fig_corr_heatmap,
                fig_pca_x_variance,
                fig_outlier_pca_x_variance,
                params["bundle_values"],
                params["measure_values"],
                Serverside(pca_df),
                Serverside(pca_outlier_df),
                Serverside(hover_data),
                no_update,
                no_update,
            )
        except Exception as e:
            return auxiliary_functions.open_modal(params, exception_message=e)
            # raise Exception(f"An error occurred while loading the scatter plot {e}")
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
            no_update,
            no_update,
            no_update,
        )


@app.callback(
    [Output("original-plot-x-y-axis", "data")],
    [Input("pca-data-store", "data"), State("graph-2-dcc", "figure")],
    background=True,
    prevent_initial_call=True,
)
def update_x_y_axes(data, figure):
    """
    Function to update the x and y axes of the scatter plot, used for the image markers
    """
    print("Updating x and y axes")
    fig = go.Figure(figure)
    return (
        Serverside(
            [
                fig.full_figure_for_development().layout.xaxis.range,
                fig.full_figure_for_development().layout.yaxis.range,
            ]
        ),
    )


@app.callback(
    [
        Output("left-image", "src"),
        Output("right-image", "src"),
        Output("table-patient-data", "data"),
    ],
    [
        Input("graph-2-dcc", "clickData"),
        Input("graph-2-dcc", "hoverData"),
        Input("image-view-axis-dropdown", "value"),
        State("hover-data-store", "data"),
    ],
)
def display_images(clickData, hoverData, axis_value, hover_data_list):
    """
    Used to access the images for the clicked and hovered points
    """
    try:

        # Extract custom data from the clickData and hoverData, if present
        # This is the FA, MD, etc. values for the clicked and hovered points
        def extract_customdata(data):
            if not data or not data.get("points", []):
                return pd.DataFrame(columns=hover_data_list)

            point_data = data["points"][0]
            if "customdata" in point_data:
                # Directly use the customdata if present
                customdata = point_data["customdata"]
                return pd.DataFrame([customdata], columns=hover_data_list)

        # Extract data for display images, category and patient
        def extract_data_for_display_images(data):
            if data is None:
                return None, None

            point_data = data["points"][0]
            if "customdata" in point_data:
                # Directly use the customdata if present
                category = data["points"][0]["customdata"][2]
                patient = data["points"][0]["customdata"][1]
                return category, patient

        # Extract data from clickData and hoverData
        click_df = extract_customdata(clickData)
        hover_df = extract_customdata(hoverData)

        # Only concatenate non-empty DataFrames
        if not click_df.empty and not hover_df.empty:
            combined_df = pd.concat([click_df, hover_df], ignore_index=True)
        elif not click_df.empty:
            combined_df = click_df
        elif not hover_df.empty:
            combined_df = hover_df
        else:
            combined_df = pd.DataFrame(columns=hover_data_list)

        # Apply transformations to Age_Group and Sex columns if they exist and are not empty
        if not combined_df.empty:
            combined_df["Age_Group"] = combined_df["Age_Group"].apply(
                auxiliary_functions.get_age_group_label
            )
            combined_df["Sex"] = combined_df["Sex"].apply(
                auxiliary_functions.get_sex_label
            )

            # Truncate float columns (excluding specified columns) to 4 decimal places
            float_columns_to_truncate = [
                col
                for col in combined_df.columns
                if col not in ["Patient", "Patient_ID", "Bundle", "Age_Group", "Sex"]
            ]
            combined_df[float_columns_to_truncate] = combined_df[
                float_columns_to_truncate
            ].apply(auxiliary_functions.truncate_float_series, axis=0)

        # Get the category, patient pairs for the clicked and hovered points
        clicked_category, clicked_patient = extract_data_for_display_images(clickData)
        hovered_category, hovered_patient = extract_data_for_display_images(hoverData)

        # Get the image URLs for the category, patient pairs
        clicked_im_url = image_backend.get_image_url(
            clicked_category, clicked_patient, axis_value, width=512, height=512
        )
        hovered_im_url = image_backend.get_image_url(
            hovered_category, hovered_patient, axis_value, width=512, height=512
        )

        return clicked_im_url, hovered_im_url, combined_df.to_dict("records")
    except Exception as e:
        return no_update, no_update, no_update


@app.callback(
    [
        Output("vtk-mesh", "state"),
        Output("vtk-volume", "state"),
        Output("vtk-view", "triggerResetCamera"),
        Output("vtk-view", "triggerRender"),
        Output("vtk-view", "background"),
    ],
    [
        Input("show-3D-bundle-for-selected-point", "n_clicks"),
        Input("graph-2-dcc", "clickData"),
        State("coloring-mode", "value"),
        State("3d-background-color-picker", "value"),
        State("cubic-spline-selector", "value"),
        State("num-spline-points", "value"),
    ],
    prevent_initial_call=True,
    running=[
        (Output("show-3D-bundle-for-selected-point", "disabled"), True, False),
    ],
    background=True,
)
def update_3d_visualization(
    n_clicks,
    clickData,
    coloring_mode,
    background_color,
    spline_selector,
    num_spline_points,
):
    time_now = datetime.datetime.now()
    """
    Function to update the 3D visualization based on the selected point (clicked point on the 2D scatter plot)
    """
    # Gets callback context
    ctx = callback_context
    # Checks if it has not been triggered
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update

    if (
        ctx.triggered_id == "show-3D-bundle-for-selected-point"
        or ctx.triggered_id == "graph-2-dcc"
    ):
        if clickData is None:
            return no_update, no_update, no_update, no_update, no_update
        else:
            # Specify the path to the new .tck file
            point_data = clickData["points"][0]
            if "customdata" in point_data:
                # Directly use the customdata if present
                clicked_category = clickData["points"][0]["customdata"][2]
                clicked_patient = clickData["points"][0]["customdata"][1]

            # Get the new .tck file path and the new .nii.gz file path
            new_tck_file_path = image_backend.get_tck_file_path(
                clicked_patient, clicked_category
            )
            new_niigz_file_path = image_backend.get_niigz_file_path(clicked_patient)

            print(new_tck_file_path)
            print(new_niigz_file_path)

            # Load the new .tck file and .nii.gz file and update the visualization
            new_mesh_state, new_volume_state = tck_file_loading.load_tck_file(
                new_tck_file_path,
                new_niigz_file_path,
                coloring_mode,
                spline_selector,
                num_spline_points,
            )
            background_color_formatted = [1, 1, 1]
            if background_color:
                try:
                    # Split the input string into a list of floats
                    hex = background_color["hex"].lstrip("#")
                    background_color_formatted = [
                        int(hex[i : i + 2], 16) / 255.0 for i in (0, 2, 4)
                    ]
                except ValueError:
                    # Handle invalid input
                    pass

            time_end = datetime.datetime.now()
            print("Time to load 3D visualization:", time_end - time_now)
            return (
                new_mesh_state,
                new_volume_state,
                random.random(),
                random.random(),
                background_color_formatted,
            )

    else:
        return no_update, no_update, no_update, no_update, no_update


@app.callback(
    [
        Output("graph-pca-scatter-plot-age-div", "children", allow_duplicate=True),
        Output("store-pca-scatter-plot-output", "data", allow_duplicate=True),
        Output("scatter-plot-knots-input", "valid", allow_duplicate=True),
        Output("scatter-plot-knots-input", "invalid", allow_duplicate=True),
    ],
    [
        Input("generate-scatter-plot-regression", "n_clicks"),
        State("scatter-plot-y-axis-dropdown", "value"),
        State("scatter-plot-color-dropdown", "value"),
        State("scatter-plot-bundle-dropdown", "value"),
        State("scatter-plot-sex-dropdown", "value"),
        State("scatter-plot-knots-input", "value"),
        State("scatter-plot-knots", "value"),
        State("pca-data-store", "data"),
        State("graph-pca-scatter-plot-age-div", "children"),
        State("store-pca-scatter-plot-output", "data"),
    ],
    prevent_initial_call=True,
)
def update_pca_scatter_plot_age(
    n_clicks,
    y_axis_value,
    color_value,
    bundle_value,
    sex_value,
    knots_value,
    enable_knots,
    pca_df,
    children,
    data_store_scatter_plot_output_json,
):
    """
    Function to calculate and display the regression of principal components against age, with different parameters
    """
    time_now = datetime.datetime.now()
    # Gets callback context
    ctx = callback_context

    # Checks if it has not been triggered
    if ctx.triggered_id != "generate-scatter-plot-regression":
        return no_update, no_update, no_update, no_update

    # Check if the PCA data is not None
    if pca_df is None:
        return no_update, no_update, no_update, no_update

    # Truncate the PCA data to the selected bundle
    pca_df_truncate = pca_df[pca_df["Bundle"] == bundle_value]

    # Check if the truncated PCA data is empty
    if len(pca_df_truncate) == 0:
        return no_update, no_update, no_update, no_update

    # Convert the Age_Group column to a categorical column, and apply the get_age_group_label function
    pca_df_truncate.loc[:, "Age_Group"] = (
        pca_df_truncate["Age_Group"]
        .astype("category")
        .apply(auxiliary_functions.get_age_group_label)
    )

    # Check if the knots are enabled
    if enable_knots:
        # Check if the knots are valid, based on the available age values
        try:
            knots_list = [int(knot) for knot in knots_value.split(",")]
        except Exception as e:
            return no_update, no_update, False, True
        knots_list = sorted(knots_list)
        min_age = pca_df["Age"].min()
        max_age = pca_df["Age"].max()
        # if the knots are not within the range of the age values, return an error
        if knots_list[0] < min_age or knots_list[-1] > max_age:
            return no_update, no_update, False, True

    # If we plot the regression with different plots, divided by sex
    if sex_value == "Divided by Sex Different Plot":
        spline_reg = principal_components_age_corr_regression_viz.SplineRegression(
            dataframe=pca_df_truncate,
            response_var=y_axis_value,
            predictor_var="Age",
            bundle_var=bundle_value,
            degree=3,
            knots=knots_list if enable_knots else None,
            method="GLM",
            by_variable="Sex",
            plots="Different Plot",
        )
    # If we plot the regression with the same plot, divided by sex
    elif sex_value == "Divided by Sex Same Plot":
        spline_reg = principal_components_age_corr_regression_viz.SplineRegression(
            dataframe=pca_df_truncate,
            response_var=y_axis_value,
            predictor_var="Age",
            bundle_var=bundle_value,
            knots=knots_list if enable_knots else None,
            degree=3,
            method="GLM",
            by_variable="Sex",
            plots="Same Plot",
        )
    # If we plot the regression with all the data
    else:
        spline_reg = principal_components_age_corr_regression_viz.SplineRegression(
            dataframe=pca_df_truncate,
            response_var=y_axis_value,
            predictor_var="Age",
            bundle_var=bundle_value,
            knots=knots_list if enable_knots else None,
            degree=3,
            method="GLM",
        )
    # print(spline_reg.fit_model())
    spline_reg.fit_model()
    # Get the plots for the regression
    figs = spline_reg.plot(
        color_column=color_value,
        hover_data=["Patient", "Patient_ID", "Bundle", "Age_Group", "Sex"],
    )
    # Get the model outputs for the regression
    models_dict_current = spline_reg.fit_model_to_df()

    # The idea here is to generate a random key for each plot generated, and store the model outputs in a dictionary, with the random key as the key
    # The random key is used to identify the plot and the model outputs
    # The model outputs are stored in a dictionary, which is then stored Serialised as a JSON object
    # This JSON object is then stored in the data store, and is used to retrieve the model outputs when the user wants to download the statistics
    # The random key is also used to identify the plot when the user wants to remove the plot
    # By removing the plot, the model outputs are also removed from the dictionary
    # The dictionary is then stored in the data store again, with the updated model outputs

    # Load the previous model outputs
    try:
        models_dict_previous = auxiliary_functions.json_to_dataframes(
            data_store_scatter_plot_output_json
        )
    except:
        # If they don't exist, create an empty dictionary
        models_dict_previous = {}

    # Create a list to store the random keys
    rand_keys = []

    # If we plot the regression with same plot, divided by sex, we need to store the model outputs for
    # two different plots, so we need to store the model outputs for each plot in the dictionary
    # But we need to store them with the same random key, so that they can be identified as the same plot
    # Basically, the random key identifies a dictionary containing the two model outputs for the same plot
    # This way, when we delete the plot, we can delete both model outputs
    # The random key is also referring to the same plot, so that the plot can be deleted
    # We have a 1-to-2 mapping between the random key and the model outputs
    # And a 1-to-1 mapping between the random key and the plot
    if sex_value == "Divided by Sex Same Plot":
        rand = random.randint(0, 100000)
        # Ensure the random number is unique
        while rand in models_dict_previous:
            rand = random.randint(0, 100000)
        model_outputs = {}
        for key, model_output in models_dict_current.items():
            model_output[f"table_1_{key}"] = model_output.pop("table_1")
            model_output[f"table_2_{key}"] = model_output.pop("table_2")
            model_outputs.update(model_output)

        # Append the current model output to the previous dictionary with a new random key
        models_dict_previous[rand] = model_outputs
        # Store the random key for use in the following loop
        rand_keys.append(rand)

    # If we plot the regression with different plots, the model outputs are stored in the dictionary with different random keys
    # The same complex logic is not needed here, as the model outputs are stored in the dictionary with different random keys
    # And we can identify the plots by the random keys, and delete the model outputs by the random keys
    # We have a 1-to-1 mapping between the random keys and the plots
    else:
        # Loop through each model's output in models_dict_current
        for _, model_output in models_dict_current.items():
            # Generate a unique random number to use as a new key
            rand = random.randint(0, 100000)

            # Ensure the random number is unique
            while rand in models_dict_previous:
                rand = random.randint(0, 100000)

            # Append the current model output to the previous dictionary with a new random key
            models_dict_previous[rand] = model_output
            # Store the random key for use in the following loop
            rand_keys.append(rand)

    print(models_dict_previous)

    # Create a Patch object to store the children
    # THis is used so we do not update the whole children list, but only the children that have been updated
    patched_children = Patch()
    for i, fig in enumerate(figs):
        # Get the random key for the current plot
        rand = rand_keys[i]

        fig_with_button = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                # Create a button to remove the plot
                                dbc.Button(
                                    "Remove",
                                    id={
                                        "type": "remove-button-",
                                        "index": rand,
                                    },  # Identify the button by the random key
                                    n_clicks=0,
                                    style={"marginTop": "40px", "width": "130%"},
                                ),
                                # Create a button to download the statistics
                                dbc.Button(
                                    "Download Stats",
                                    id={
                                        "type": "download-stats-button-",
                                        "index": rand,  # Identify the button by the random key
                                    },
                                    n_clicks=0,
                                    style={"marginTop": "10px", "width": "130%"},
                                ),
                                # Create a download object to download the statistics via the button
                                dcc.Download(
                                    id={"type": "download-stats-output-", "index": rand}
                                ),
                            ],
                            width=1,
                        ),
                        dbc.Col(
                            # The plot is displayed here
                            dcc.Graph(
                                id={
                                    "type": "graph-pca-scatter-plot-age-",
                                    "index": rand,
                                },
                                figure=fig,
                                clear_on_unhover=True,
                                style={"height": "600px"},
                                config=IMAGE_DOWNLOAD_OPTIONS,  # Set the download options for the plot, defined in the constants file
                            ),
                            width=11,
                        ),
                    ],
                ),
            ]
        )
        # Append the plot to the Patch object
        patched_children.append(fig_with_button)
    time_end = datetime.datetime.now()
    print("Time to generate regression plots:", time_end - time_now)

    return [
        patched_children,  # Return the Patch object with the children
        auxiliary_functions.dataframes_to_json(
            models_dict_previous
        ),  # Store the model outputs in the data store
        no_update,
        no_update,
    ]


@app.callback(
    [
        Output("graph-pca-scatter-plot-age-div", "children"),
        Output("store-pca-scatter-plot-output", "data", allow_duplicate=True),
    ],
    [Input({"type": "remove-button-", "index": ALL}, "n_clicks")],
    [
        State({"type": "remove-button-", "index": ALL}, "id"),
        State("graph-pca-scatter-plot-age-div", "children"),
        State("store-pca-scatter-plot-output", "data"),
    ],
    prevent_initial_call=True,
)
def remove_plot(n_clicks, id, children, data_store_scatter_plot_output_json):
    """
    This function is used to remove a plot from the PCA scatter plot regression tab
    And also remove the model outputs from the data store, based on the random key, which is used to identify the plot and the model outputs
    The random key is given in the id of the button that is clicked
    """
    # Load the model outputs from the data store
    data_store_scatter_plot_output_df = auxiliary_functions.json_to_dataframes(
        data_store_scatter_plot_output_json
    )
    # Get the callback context
    ctx = callback_context

    # For each button that was clicked
    for item in ctx.triggered:
        # Get the random key from the id of the button
        prop_id_dict = eval(item["prop_id"].split(".")[0])
        index = prop_id_dict["index"]
        type_ = prop_id_dict["type"]
        value = item["value"]
    # If the type of the button is remove-button- and the value is not 0 (the button was clicked)
    if type_ == "remove-button-" and value != 0:
        # Loop through the children
        for i, child in enumerate(children):
            # Get the random key of the child
            prop_id_dict_child = auxiliary_functions.find_key_in_nested_dict(
                child, "index"
            )
            if (
                prop_id_dict_child == index
            ):  # If the random key of the child is the same as the random key of the button
                if (
                    data_store_scatter_plot_output_df
                    and str(index) in data_store_scatter_plot_output_df
                ):
                    del data_store_scatter_plot_output_df[
                        str(index)
                    ]  # Remove the model outputs from the dictionary
                # Remove the child from the children
                children.pop(i)
                return [
                    children,  # Return the updated children
                    auxiliary_functions.dataframes_to_json(
                        data_store_scatter_plot_output_df
                    ),  # Return the updated model outputs
                ]
    return no_update, no_update


@app.callback(
    Output({"type": "download-stats-output-", "index": MATCH}, "data"),
    [
        Input({"type": "download-stats-button-", "index": MATCH}, "n_clicks"),
        Input({"type": "download-stats-button-", "index": MATCH}, "id"),
    ],
    [
        State("store-pca-scatter-plot-output", "data"),
    ],
    prevent_initial_call=True,
)
def download_file_pca_scatter_plot_age_output(
    n_clicks, index_dict, data_store_scatter_plot_output_json
):
    """
    Function to download the statistics for the PCA scatter plot regression
    Based on the same concept as the remove plot function, the random key is used to identify the model outputs
    """

    # If there is nothing to download, return no_update
    if data_store_scatter_plot_output_json is None:
        return no_update

    # Get the model outputs from the data store
    data_store_scatter_plot_output_dfs = auxiliary_functions.json_to_dataframes(
        data_store_scatter_plot_output_json
    )

    print(data_store_scatter_plot_output_dfs)
    print(index_dict)

    # Get the model outputs for the random key
    data_store_scatter_plot_output_df = data_store_scatter_plot_output_dfs.pop(
        str(index_dict["index"])
    )

    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    # Open the Excel writer
    writer = pd.ExcelWriter(output, engine="xlsxwriter")

    # Write the model outputs to the Excel file
    for key, df in data_store_scatter_plot_output_df.items():
        if key.startswith(
            "table_"
        ):  # This is used in case there are multiple tables for the same plot
            df.to_excel(writer, sheet_name=key, index=True)

    # Close the writer
    writer.close()
    # Seek to the beginning of the BytesIO object
    data = output.getvalue()

    # Return the Excel file
    return dcc.send_bytes(data, "mydf.xlsx")


@app.callback(
    [
        Output("offcanvas-patient-selector", "is_open"),
        Output("offcanvas-3D-bundle-visualization", "is_open"),
    ],
    [
        Input("open-offcanvas-patient-selector", "n_clicks"),
        Input("open-offcanvas-3D-bundle-visualization", "n_clicks"),
    ],
    [
        State("offcanvas-patient-selector", "is_open"),
        State("offcanvas-3D-bundle-visualization", "is_open"),
    ],
)
def toggle_collapse(
    n_patient_selector,
    n_3d_bundle,
    is_open_patient_selector,
    is_open_3d_bundle,
):
    """
    Toggle the offcanvas for the patient selector and the 3D bundle visualization
    """
    # Gets callback context
    ctx = callback_context

    # Checks if it has not been triggered
    if not ctx.triggered:
        return no_update, no_update
    # Check if the offcanvas for the patient selector was triggered
    if ctx.triggered_id == "open-offcanvas-patient-selector":
        return not is_open_patient_selector, no_update
    # Check if the offcanvas for the 3D bundle visualization was triggered
    if ctx.triggered_id == "open-offcanvas-3D-bundle-visualization":
        return no_update, not is_open_3d_bundle


@app.callback(
    [Output("range-area", "style"), Output("list-area", "style")],
    [Input("selection-mode", "value")],
)
def update_input_area(selection_mode):
    """
    This is used in the patient selector to determine if the input area for the patient list or the input area for the patient range is displayed
    """
    if selection_mode == "range":
        return [{"display": "block"}, {"display": "none"}]
    elif selection_mode == "list":
        return [{"display": "none"}, {"display": "block"}]


@app.callback(
    [Output("age-group-area", "style"), Output("age-range-area", "style")],
    [Input("age-mode", "value")],
)
def update_age_area(selection_mode):
    """
    This is used in the patient selector to determine if the input area for the age group or the input area for the age range is displayed, or both
    """
    if selection_mode == "age-group":
        return [{"display": "block"}, {"display": "none"}]
    elif selection_mode == "age-range":
        return [{"display": "none"}, {"display": "block"}]
    elif selection_mode == "all":
        return [{"display": "block"}, {"display": "block"}]


@app.callback(
    Output("scatter-plot-knots-collapse", "style"),
    [Input("scatter-plot-knots", "value")],
    prevent_initial_call=True,
)
def toggle_collapse_knots(value):
    """
    Toggle the collapse for the knots input, in the PCA scatter plot regression tab
    """
    if value:
        # If there's a value, open the collapse
        return {"display": "block"}
    else:
        # If there's no value, collapse it
        return {"display": "none"}


@app.callback(
    [
        Output("scatter-plot-knots-input", "valid", allow_duplicate=True),
        Output("scatter-plot-knots-input", "invalid", allow_duplicate=True),
    ],
    [
        Input("scatter-plot-knots-input", "value"),
        State("scatter-plot-knots-input", "pattern"),
    ],
    prevent_initial_call=True,
)
def check_knots(value, pattern):
    """
    Check if the knots input is valid, based on the pattern in the content_layout folder
    """
    patt = re.compile(pattern)
    if not value:
        return no_update, no_update
    if patt.match(value):
        return True, False
    return False, True


@app.callback(
    [
        Output("input-significance-level", "valid", allow_duplicate=True),
        Output("input-significance-level", "invalid", allow_duplicate=True),
    ],
    [
        Input("input-significance-level", "value"),
        State("input-significance-level", "pattern"),
    ],
    prevent_initial_call=True,
)
def check_input_significance_level(value, pattern):
    """
    Check if the significance level input is valid, based on the pattern in the content_layout folder
    """
    patt = re.compile(pattern)
    if not value:
        return no_update, no_update
    if patt.match(str(value)):
        return True, False
    return False, True


@app.callback(
    [
        Output("input-stratified-sampling", "valid", allow_duplicate=True),
        Output("input-stratified-sampling", "invalid", allow_duplicate=True),
        Output("input-stratified-sampling-2", "valid", allow_duplicate=True),
        Output("input-stratified-sampling-2", "invalid", allow_duplicate=True),
    ],
    [
        Input("input-stratified-sampling", "value"),
        Input("input-stratified-sampling-2", "value"),
        State("input-stratified-sampling", "pattern"),
        State("input-stratified-sampling-2", "pattern"),
    ],
    prevent_initial_call=True,
)
def check_stratified_sampling_splom_plot_percentage(value1, value2, pattern1, pattern2):
    """
    Check if the input stratified percentage inputs are valid, based on the patterns in the content_layout folder
    """
    patt1 = re.compile(pattern1)
    patt2 = re.compile(pattern2)

    # Default responses for both inputs
    valid1, invalid1 = no_update, no_update
    valid2, invalid2 = no_update, no_update

    # Check first input
    if value1:
        if patt1.match(str(value1)):
            valid1, invalid1 = True, False
        else:
            valid1, invalid1 = False, True

    # Check second input
    if value2:
        if patt2.match(str(value2)):
            valid2, invalid2 = True, False
        else:
            valid2, invalid2 = False, True

    return valid1, invalid1, valid2, invalid2


@app.callback(
    [
        Output("input-nu-level", "valid", allow_duplicate=True),
        Output("input-nu-level", "invalid", allow_duplicate=True),
    ],
    [
        Input("input-nu-level", "value"),
        State("input-nu-level", "pattern"),
    ],
    prevent_initial_call=True,
)
def check_nu_level(value, pattern):
    """
    Check if the nu level input is valid, based on the pattern in the content_layout folder
    """
    patt = re.compile(pattern)
    if not value:
        return no_update, no_update
    if patt.match(str(value)):
        return True, False
    return False, True


@app.callback(
    [
        Output("dropdown-bundle-outlier-detection", "options"),
        Output("dropdown-age-group-outlier-detection", "options"),
    ],
    [Input("pca-data-store", "data")],
)
def outlier_dropdowns_update(pca_df):
    """
    Update the dropdowns for the bundle and age group in the outlier detection tab, based on the PCA data
    """
    if pca_df is None:
        return no_update, no_update
    bundle_options, _, age_group_options, _ = (
        auxiliary_functions.prepare_dropdown_options(pca_df)
    )
    return [bundle_options, age_group_options]


@app.callback(
    [Output("table-outlier-data", "data"), Output("outlier-points-store", "data")],
    [Input("button-detect-outliers", "n_clicks")],
    [
        State("dropdown-bundle-outlier-detection", "value"),
        State("dropdown-age-group-outlier-detection", "value"),
        State("pca-outlier-store", "data"),
        State("input-significance-level", "value"),
        State("input-nu-level", "value"),
        State("n_components_to_use_for_outlier", "value"),
    ],
    background=True,
    prevent_initial_call=True,
    running=[
        (Output("button-detect-outliers", "disabled"), True, False),
    ],
)
def outlier_generation(
    n_clicks,
    bundle_value,
    age_group_value,
    pca_df,
    significance,
    nu,
    n_components,
):
    """
    Function to generate the outliers based on the PCA data, and the parameters selected by the user
    """
    # If one of the inputs is None, return no_update
    if pca_df is None or significance is None or nu is None:
        return no_update, no_update
    print(n_components)

    # Truncate the PCA data to the selected bundle and age group
    pca_df_truncate = outlier_detection.pca_truncate_for_anomaly_detector(
        pca_df, bundle_value, age_group_value
    )
    # Generate the outliers
    outlier_df = outlier_detection.anomaly_detector_caller(
        pca_df_truncate,
        int(n_components),  # Convert the n_components to an integer
        1 - (float(significance) / 100.0),  # Convert the significance to a float
        (float(nu) / 100.0),  # Convert the nu to a float
    )
    return [
        auxiliary_functions.truncate_floats_in_df(outlier_df).to_dict(
            "records"
        ),  # Return the outliers as a dictionary for the table
        Serverside(
            outlier_df
        ),  # Return the outliers as a Serverside object for further use
    ]


@app.callback(
    [Output("graph-outlier-detection", "figure"), Output("graph-2-dcc", "figure")],
    [
        Input("outlier-points-store", "data"),
        Input("load-outliers-on-plot", "value"),
    ],
    [
        State("dropdown-bundle-outlier-detection", "value"),
        State("dropdown-age-group-outlier-detection", "value"),
        State("pca-outlier-store", "data"),
        State("pca-data-store", "data"),
        State("graph-2-dcc", "figure"),
        State("dropdown-x-axis-outlier", "value"),
        State("dropdown-y-axis-outlier", "value"),
    ],
    prevent_initial_call=True,
)
def outlier_graph_update(
    outlier_df,
    load_outliers,
    bundle_value,
    age_group_value,
    pca_outlier_df,
    pca_df,
    fig_original,
    x_axis_value,
    y_axis_value,
):
    """
    Update the PCA scatter plot and the plot in the outlier tab with the visualizations for the outliers
    """
    hover_data = ["Patient", "Patient_ID", "Bundle", "Age_Group", "Age", "Sex"]
    # print(fig_original)
    if pca_df is None or outlier_df is None:
        return [no_update, no_update]

    # Truncate the PCA data to the selected bundle and age group
    pca_outlier_df_truncate = outlier_detection.pca_truncate_for_anomaly_detector(
        pca_outlier_df, bundle_value, age_group_value
    )

    num1 = x_axis_value.replace("PC", "")
    num2 = y_axis_value.replace("PC", "")

    # Create the labels dictionary
    labels = {
        x_axis_value: f"Principal Component {num1}",
        y_axis_value: f"Principal Component {num2}",
    }

    # This part is used to generate the PCA scatter plot in the outlier tab
    fig = dim_reduction_viz.create_pca_scatter_plot(
        pca_outlier_df_truncate,
        x=x_axis_value,
        y=y_axis_value,
        color="Bundle",
        hover_data=hover_data,
        labels=labels,
        title="2D Scatter Plot with PCA",
    )

    if load_outliers:
        # If the user wants to load the outliers on the plot
        # Merge the dataframes based on 'Patient_ID' and 'Bundle'
        condition = (pca_df["Patient_ID"].isin(outlier_df["Patient_ID"])) & (
            pca_df["Bundle"].isin(outlier_df["Bundle"])
        )
        merged_df = pca_df[condition]
        # print(merged_df)

        # Add the outliers to the PCA scatter plot
        fig.add_trace(
            go.Scatter(
                x=outlier_df[x_axis_value],
                y=outlier_df[y_axis_value],
                mode="markers",
                marker=dict(color="red", size=10, symbol="cross"),
                name="Outliers",
                hoverinfo="skip",
            )
        )
        fig_pca = (
            Patch()
        )  # Create a Patch object to store the figure, so we do not update the whole figure, but only the updated part
        # print(fig_original)
        for i, trace in enumerate(fig_original["data"]):
            if (
                "name" in trace and trace["name"] == "Outliers"
            ):  # If the trace is an outlier trace
                fig_pca["data"][i].clear()  # Clear the trace

        # This part is used to generate the plot in the PCA scatter plot tab
        patch = go.Scatter(
            x=merged_df["PC1"],
            y=merged_df["PC2"],
            mode="markers",
            marker=dict(color="red", size=10, symbol="cross"),
            name="Outliers",
            hoverinfo="skip",  # Do not show the hover info, so the old hover info is still displayed
        )
        fig_pca["data"].append(patch)  # Append the trace to the Patch object
        return fig, fig_pca

    return fig, no_update


@app.callback(
    Output("graph-2-dcc", "figure", allow_duplicate=True),
    [Input("load-outliers-on-plot", "value"), Input("outlier-points-store", "data")],
    [State("graph-2-dcc", "figure")],
    prevent_initial_call=True,
)
def update_original_plot_with_outliers(load_outliers, _, fig_original):
    """
    This function is used to only remove the outliers from the PCA scatter plot, when the user does not want to load the outliers on the plot
    """
    # If the user wants to load the outliers on the plot, we do not update, because the outliers are already loaded
    if load_outliers:
        return no_update
    else:  # If the user does not want to load the outliers on the plot, we must remove the outliers from the plot
        fig_pca = Patch()
        for i, trace in enumerate(fig_original["data"]):
            if "name" in trace and trace["name"] == "Outliers":
                fig_pca["data"][i].clear()
        return fig_pca


@app.callback(
    Output("n_components_to_use_for_outlier", "options"),
    Output("dropdown-x-axis-outlier", "options"),
    Output("dropdown-y-axis-outlier", "options"),
    [Input("pca-outlier-store", "data")],
    prevent_initial_call=True,
)
def update_outlier_n_components_dropdown(pca_outlier_df):
    """
    Update the dropdown for the number of components to use for outlier detection, based on the PCA data
    """
    # Filter column names
    pc_columns = [col for col in pca_outlier_df.columns if col.startswith("PC")]

    # Extract numbers and convert to integers
    pc_numbers = [
        int(col[2:]) for col in pc_columns if col[2:].isdigit() and col[2:] != "1"
    ]

    # Sort numbers just in case they are not in order
    pc_numbers.sort()

    return pc_numbers, pc_columns, pc_columns


@app.callback(
    [
        Output("modal_about", "is_open"),
        Output("modal_contact", "is_open"),
        Output("url", "pathname"),
    ],
    [
        Input("url", "pathname"),
        Input("close-about", "n_clicks"),
        Input("close-contact", "n_clicks"),
    ],
    [State("modal_about", "is_open"), State("modal_contact", "is_open")],
    prevent_initial_call=True,
)
def toggle_about_contact_modals(
    pathname, close_about_clicks, close_contact_clicks, is_about_open, is_contact_open
):
    """
    Function to toggle the about and contact modals from the navigation bar
    Logic is based on the pathname and the close buttons in the modals
    The close buttons are used to close the modals, and the pathname is used to open the modals
    """
    ctx = callback_context
    if not ctx.triggered:
        return [no_update, no_update, no_update]
    elif ctx.triggered_id == "url":
        print(is_about_open, is_contact_open, pathname)
        if pathname == "/about":
            return [not is_about_open, is_contact_open, "/about"]
        if pathname == "/contact":
            return [is_about_open, not is_contact_open, "/contact"]
        else:
            print(is_about_open, is_contact_open, pathname)
            return [is_about_open, is_contact_open, "/"]
    elif ctx.triggered_id == "close-about":
        return [not is_about_open, is_contact_open, "/"]
    elif ctx.triggered_id == "close-contact":
        return [is_about_open, not is_contact_open, "/"]


@app.callback(
    Output("table-outlier-data", "css"),
    Input("table-outlier-data", "derived_virtual_data"),
)
def style_export_button(data):
    if data == []:
        return [{"selector": ".export", "rule": "display:none"}]
    else:
        return [{"selector": ".export", "rule": "display:block"}]


if __name__ == "__main__":
    app.run(debug=True, port=8051, processes=4, threaded=False)
