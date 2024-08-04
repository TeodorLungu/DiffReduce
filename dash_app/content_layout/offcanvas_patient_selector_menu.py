import dash_bootstrap_components as dbc
from dash import dcc, html

offcanvas_patient_selector = dbc.Offcanvas(
    html.Div(
        [
            dbc.Label(
                "Select the mode for patient selection",
                style={"font-weight": "bold"},
            ),
            dbc.RadioItems(
                id="selection-mode",
                options=[
                    {
                        "label": "Range",
                        "value": "range",
                    },
                    {
                        "label": "List",
                        "value": "list",
                    },
                ],
                value="range",  # Default value
                labelStyle={"display": "block"},
            ),
            dbc.Collapse(
                id="range-area",
                children=[
                    dbc.Row(
                        [
                            dbc.Label(
                                "Begin Index",
                                html_for="begin-index",
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    type="number",
                                    id="begin-index",
                                    value=0,
                                    min=0,
                                    placeholder="Enter Begin Index",
                                    style={
                                        "textAlign": "center",
                                        "width": "100%",
                                    },
                                ),
                                width=8,
                            ),
                        ],
                        style={"marginTop": "10px"},
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label(
                                "End Index",
                                html_for="end-index",
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    type="number",
                                    id="end-index",
                                    value=100,
                                    min=0,
                                    placeholder="Enter End Index",
                                    style={
                                        "textAlign": "center",
                                        "width": "100%",
                                    },
                                ),
                                width=8,
                            ),
                        ],
                        style={"marginTop": "10px"},
                        className="mb-3",
                    ),
                ],
            ),
            dbc.Collapse(
                id="list-area",
                children=[
                    dbc.Label("Patient Indices (comma-separated)"),
                    dbc.Input(
                        id="list-index",
                        type="text",
                        value="",
                        style={
                            "textAlign": "center",
                            "width": "100%",
                        },
                    ),
                ],
            ),
            html.Hr(),
            dbc.Label(
                "Select the mode for age selection",
                style={"font-weight": "bold"},
            ),
            dbc.RadioItems(
                id="age-mode",
                options=[
                    {
                        "label": "Age Group",
                        "value": "age-group",
                    },
                    {
                        "label": "Age Range",
                        "value": "age-range",
                    },
                    {
                        "label": "Age Group and Range",
                        "value": "all",
                    },
                ],
                value="age-group",  # Default value
                labelStyle={"display": "block"},
            ),
            dbc.Collapse(
                [
                    html.Br(),
                    dbc.Label(
                        "Select the Age Group",
                        style={"font-weight": "bold"},
                    ),
                    dcc.Dropdown(
                        id="age-group-dropdown",
                        options=[],
                        multi=True,
                        className="dbc",
                    ),
                ],
                className="dbc",
                id="age-group-area",
            ),
            dbc.Collapse(
                [
                    html.Br(),
                    dbc.Label(
                        "Select the Age Range",
                        style={"font-weight": "bold"},
                    ),
                    html.Br(),
                    dbc.Label("Begin Age"),
                    dbc.Input(
                        id="begin-age",
                        type="number",
                        min=0,
                        max=101,
                        value=0,
                        style={
                            "textAlign": "center",
                            "width": "100%",
                        },
                    ),
                    dbc.Label("End Age"),
                    dbc.Input(
                        id="end-age",
                        type="number",
                        value=100,
                        min=0,
                        max=101,
                        style={
                            "textAlign": "center",
                            "width": "100%",
                        },
                    ),
                ],
                id="age-range-area",
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Label(
                        "Select the Sex",
                        style={"font-weight": "bold"},
                    ),
                    dcc.Dropdown(
                        id="sex-dropdown",
                        options=[],
                        multi=True,
                        className="dbc",
                    ),
                ],
                className="dbc",
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Label(
                        "Select the bundles",
                        style={"font-weight": "bold"},
                    ),
                    dcc.Dropdown(
                        id="bundle-dropdown",
                        options=[],
                        multi=True,
                        className="dbc",
                    ),
                    html.Br(),
                    dbc.Label(
                        "Select the measures",
                        style={"font-weight": "bold"},
                    ),
                    dcc.Dropdown(
                        id="measure-dropdown",
                        options=[],
                        multi=True,
                        className="dbc",
                    ),
                ],
                className="dbc",
            ),
            html.Hr(),
            html.Div(
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                dbc.Label(
                                    "The SPLOM plot can become cluttered depending on the number of points. This option applies stratified sampling to the SPLOM plot, defaulting to no stratification. Please select the percentage of samples per bundle. The percentage must be between 1 and 100."
                                ),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="input-stratified-sampling",
                                            placeholder="Select Percentage",
                                            type="number",
                                            pattern="^(100|[1-9][0-9]?)$",
                                        ),
                                        dbc.InputGroupText("%"),
                                    ],
                                    className="mb-3",
                                ),
                            ],
                            title="Stratified Sampling for SPLOM Plot",
                        ),
                    ],
                ),
            ),
            html.Hr(),
            dbc.Label(
                "Select whether to load only data for which 3D images are available \n regardless of the selected range or list."
            ),
            dbc.Switch(
                id="load-real-data-selector",
                value=False,
                label="Load only data with 3D images",
            ),
            html.Hr(),
            dbc.Label(
                "Apply changes to the data.",
                style={"font-weight": "bold"},
            ),
            dbc.Button(
                "Apply Changes",
                id="apply-changes-button",
                n_clicks=0,
                style={
                    "textAlign": "center",
                    "width": "100%",
                },
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Error Encountered!")),
                    dbc.ModalBody(
                        "",
                        id="modal_patient_selector_error_body",
                        style={"whiteSpace": "pre-line"},
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="modal_patient_selector_close",
                            className="ms-auto",
                            n_clicks=0,
                        )
                    ),
                ],
                id="modal_patient_selector_error",
                is_open=False,
            ),
        ]
    ),
    id="offcanvas-patient-selector",
    title="Patient Selector",
    is_open=False,
)
