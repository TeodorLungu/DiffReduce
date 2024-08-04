import dash_bootstrap_components as dbc
from dash import dcc, html

pca_scatter_plot_row = [
    dcc.Store("store-pca-scatter-plot-output"),
    dbc.Row(
        dbc.Col(
            html.H5(
                "Age versus PCA Components",
                className="text-center mt-2",
            ),
            width={
                "size": 6,
                "offset": 3,
            },
        ),
    ),
    dbc.Row(
        dbc.Col(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(
                                "This tool enables users to generate interactive scatter plots with Principal Component Analysis (PCA) components, providing intuitive controls for customizing the visualization and conducting regression analysis."
                            ),
                            html.H5("Interactive Scatter Plot Customization"),
                            html.Ol(
                                [
                                    html.Li(
                                        "Axis Customization: Users can select which PCA component to display on the y-axis to tailor the analysis to specific needs."
                                    ),
                                    html.Li(
                                        "Color Coding: Plots can be color-coded based on age or age groups, allowing for visual differentiation and analysis."
                                    ),
                                    html.Li(
                                        "Data Filtering: Flexibility to filter the scatter plot by bundles and sex, with options to view all data together or in separate plots by sex."
                                    ),
                                ]
                            ),
                            html.H5("Regression Analysis Features"),
                            html.Ul(
                                [
                                    html.Li(
                                        "Knot Configuration: Users can include and position knots in the spline regression to enhance the model's adaptability."
                                    ),
                                    html.Li(
                                        "Tooltip Assistance: Guidance on knot positioning is available via a tooltip. Of note is that knots are optional and can be omitted if not needed."
                                    ),
                                ]
                            ),
                            html.H5("Data Visualization and Insights"),
                            html.Ul(
                                [
                                    html.Li(
                                        "Regression Lines and Confidence Intervals: Visual representation includes regression lines with confidence intervals."
                                    ),
                                ]
                            ),
                            html.H5("Generalized Linear Models (GLM)"),
                            html.P(
                                "The regression tool supports the Generalized Linear Models (GLM) method, applying it to the entire dataset or selected subsets based on specific variables such as sex, along with detailed performance metrics."
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        "Downloadable Results: Users can download the full regression summary as an Excel file for further analysis and reporting."
                                    ),
                                    html.Li(
                                        "Performance Evaluation: Diagnostic metrics, including R-squared and p-values, are provided to assess the model's performance and significance."
                                    ),
                                ]
                            ),
                        ],
                        title="Functionality Description",
                    ),
                ],
                start_collapsed=True,
                style={"marginBottom": "10px"},
            ),
        ),
    ),
    dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id="scatter-plot-y-axis-dropdown",
                    options=[
                        "PC1",
                        "PC2",
                    ],
                    value="PC1",
                    multi=False,
                    className="dbc",
                ),
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="scatter-plot-color-dropdown",
                    options=[
                        "Age",
                        "Age_Group",
                    ],
                    value="Age",
                    multi=False,
                    className="dbc",
                ),
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="scatter-plot-bundle-dropdown",
                    multi=False,
                    className="dbc",
                ),
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="scatter-plot-sex-dropdown",
                    options=[
                        "All",
                        "Divided by Sex Different Plot",
                        "Divided by Sex Same Plot",
                    ],
                    multi=False,
                    className="dbc",
                )
            ),
            dbc.Col(
                dbc.Button(
                    "Generate Scatter Plot",
                    id="generate-scatter-plot-regression",
                    n_clicks=0,
                    style={
                        "textAlign": "center",
                        "width": "100%",
                    },
                ),
            ),
        ]
    ),
    dbc.Row(
        dbc.Col(
            [
                dbc.Col(
                    dbc.Checkbox(
                        id="scatter-plot-knots",
                        label="Use Knots in Regression",
                        value=False,
                    ),
                ),
                dbc.Collapse(
                    id="scatter-plot-knots-collapse",
                    children=[
                        dbc.Input(
                            id="scatter-plot-knots-input",
                            type="text",
                            pattern="^\s*\d+\s*(,\s*\d+\s*)*$",
                            valid=False,
                        ),
                        dbc.Tooltip(
                            "Enter numbers separated by a comma. Example: 10, 20, 30",
                            id="tooltip",
                            is_open=False,
                            target="scatter-plot-knots-input",
                            trigger="hover",
                        ),
                    ],
                    is_open=False,
                ),
            ],
            style={
                "margin-top": "20px",
            },
        ),
        style={"margin-bottom": "50px"},
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    children=[],
                    id="graph-pca-scatter-plot-age-div",
                ),
            ),
        ],
    ),
]
