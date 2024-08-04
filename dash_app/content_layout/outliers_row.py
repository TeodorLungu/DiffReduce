import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

outliers_row = [
    dbc.Row(
        dbc.Col(
            html.H5(
                "Outlier Detection",
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
                                "Outlier detection identifies data points that deviate significantly from the overall pattern of the dataset. "
                                "This tool uses a robust multi-step approach to minimize the influence of outliers and reduce data dimensionality."
                            ),
                            html.H5("Two-Step Approach"),
                            html.Ol(
                                [
                                    html.Li(
                                        "Quantile Transformation: This step minimizes the influence of outliers by transforming the data distribution to be more Normal."
                                    ),
                                    html.Li(
                                        "Principal Component Analysis (PCA): PCA reduces the dimensionality of the transformed data."
                                    ),
                                    html.Li(
                                        "Mahalanobis Distance with Robust Estimators: After applying PCA, the Mahalanobis distance is computed using a robust estimator, "
                                        "Minimum Covariance Determinant (MCD). This helps to measure the distance of each data point from the mean while minimizing the impact of outliers. "
                                        "A significance level is set to establish a threshold, beyond which data points are classified as outliers."
                                    ),
                                    html.Li(
                                        "One-Class SVM (OCSVM): Using the cleaned data (data without detected outliers from the Mahalanobis distance), "
                                        "an OCSVM with an RBF kernel is trained to identify finer anomalies, ensuring no more than a selected percentage ν of the data is excluded as outliers."
                                    ),
                                ]
                            ),
                            html.H5("User Interaction and Output"),
                            html.Ul(
                                [
                                    html.Li(
                                        "Select bundles and age groups for outlier detection. These selections can be optional."
                                    ),
                                    html.Li(
                                        "Set the significance level for the Mahalanobis Distance, set the expected outlier percentage in the dataset and choose the number of PCA components."
                                    ),
                                    html.Li(
                                        "Select the x-axis and y-axis PCA components for the scatter plot. Selecting different components can provide different perspectives on the data, and a visual explanation of the detected outliers."
                                    ),
                                    html.Li(
                                        "Results: A table displays the detected outliers, a scatter plot highlights outliers with red crosses,  "
                                        "and an explained variance plot shows the cumulative explained variance of the PCA components to help determine the number of components to use. Generally, more components capture finer details of the data, but fewer components are preferred for a more general overview."
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
                    id="dropdown-bundle-outlier-detection",
                    multi=False,
                    className="dbc",
                ),
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="dropdown-age-group-outlier-detection",
                    multi=False,
                    className="dbc",
                ),
            ),
            dbc.Col(
                [
                    dbc.Switch(
                        id="load-outliers-on-plot",
                        value=False,
                        label="View Outliers on Plot",
                        style={
                            "margin": "10px",
                        },
                    ),
                    dcc.Store(id="outlier-points-store"),
                ],
            ),
            dbc.Col(
                [
                    dcc.Dropdown(
                        id="n_components_to_use_for_outlier",
                        placeholder="No. Components",
                        multi=False,
                        className="dbc",
                    ),
                ],
            ),
            dbc.Col(
                dbc.Button(
                    "Detect Outliers",
                    id="button-detect-outliers",
                    n_clicks=0,
                    style={
                        "textAlign": "center",
                        "width": "100%",
                    },
                ),
            ),
        ],
        style={"marginBottom": "10px"},
    ),
    dbc.Row(
        [
            dbc.Col(
                children=[
                    dbc.InputGroup(
                        [
                            dbc.Input(
                                id="input-significance-level",
                                placeholder="Significance",
                                type="number",
                                pattern="^([1-9]?[0-9](\.[0-9]{1,2})?|0?(\.[0-9]{1,2})?)$",
                            ),
                            dbc.InputGroupText("%"),
                        ],
                        className="mb-3",
                    ),
                    dbc.Tooltip(
                        "Significance Level for Mahalanobis Distance (Usually 95% or 99%)",
                        id="tooltip_significance_level",
                        is_open=False,
                        target="input-significance-level",
                        trigger="hover",
                    ),
                ],
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.Input(
                            id="input-nu-level",
                            placeholder="Expected Outliers",
                            type="number",
                            pattern="^([1-9]?[0-9](\.[0-9]{1,2})?|0?(\.[0-9]{1,2})?)$",
                        ),
                        dbc.InputGroupText("%"),
                        dbc.Tooltip(
                            "Expected Outlier Percentage in Dataset for OCSVM (Usually 1%, 5%, or 10%)",
                            id="tooltip_nu_level",
                            is_open=False,
                            target="input-nu-level",
                            trigger="hover",
                        ),
                    ],
                    className="mb-3",
                ),
            ),
        ],
        style={"marginBottom": "10px"},
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("X-axis Principal Component"),
                                width=3,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="dropdown-x-axis-outlier",
                                    multi=False,
                                    className="dbc",
                                ),
                                width=8,
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("Y-axis Principal Component"),
                                width=3,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="dropdown-y-axis-outlier",
                                    multi=False,
                                    className="dbc",
                                ),
                                width=8,
                            ),
                        ]
                    ),
                ],
            ),
        ],
        style={"marginBottom": "50px"},
    ),
    dbc.Row(
        dbc.Col(
            [
                dash_table.DataTable(
                    id="table-outlier-data",
                    style_table={"overflowX": "scroll"},
                    export_format="csv",
                ),
            ]
        ),
    ),
    dbc.Row(
        dbc.Col(
            [
                dcc.Graph(
                    id="graph-outlier-detection",
                    style={"height": "600px"},
                ),
            ]
        ),
    ),
    dbc.Row(
        dbc.Col(
            [
                dcc.Graph(
                    id="graph-explained-outlier-variance",
                    style={"height": "600px"},
                ),
            ],
        ),
    ),
]
