import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html
from PIL import Image

from constants import IMAGE_DOWNLOAD_OPTIONS, LOGO
from content_layout.image_hovering_row import image_hovering
from content_layout.outliers_row import outliers_row
from content_layout.pca_loadings_row import pca_loadings_row
from content_layout.pca_scatter_plot_row import pca_scatter_plot_row
from content_layout.sidebar_navigation import sidebar_layout
from content_layout.viz_3d_row import viz_3d_row


def create_content_layout():
    fig = px.scatter()
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    content_layout = html.Div(
        [
            dbc.Navbar(
                dbc.Container(
                    [
                        html.A(
                            dbc.Row(
                                [
                                    dcc.Location(id="url", refresh=False),
                                    dbc.Col(
                                        html.Img(src=Image.open(LOGO), height="30px")
                                    ),
                                    dbc.Col(
                                        dbc.NavbarBrand("DiffReduce", className="ms-2")
                                    ),
                                ],
                                align="center",
                                className="g-0",
                            ),
                            href="/",
                            style={"textDecoration": "none"},
                        ),
                        dbc.Row(
                            [
                                dbc.NavbarToggler(id="navbar-toggler"),
                                dbc.Collapse(
                                    dbc.Nav(
                                        [
                                            dbc.NavItem(dbc.NavLink("Home", href="/")),
                                            dbc.NavItem(
                                                dbc.NavLink("About", href="/about")
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink("Contact", href="/contact")
                                            ),
                                        ],
                                        className="w-100",
                                    ),
                                    id="navbar-collapse",
                                    is_open=False,
                                    navbar=True,
                                ),
                            ],
                            className="flex-row-reverse",
                        ),
                    ],
                    style={
                        "marginLeft": "10px",
                        "marginRight": "10px",
                        "max-width": "none",
                    },
                ),
                color="var(--bs-gray-200)",
                dark=False,
                style={"max-width": "none", "width": "100%"},
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                sidebar_layout,
                                width=2,
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Div(
                                            className="container",
                                            children=[
                                                dbc.Container(
                                                    fluid=True,
                                                    children=[
                                                        dbc.Tabs(
                                                            [
                                                                dbc.Tab(
                                                                    dbc.Card(
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    dcc.Graph(
                                                                                        id="graph-2-dcc",
                                                                                        figure=fig,
                                                                                        clear_on_unhover=False,
                                                                                        config=IMAGE_DOWNLOAD_OPTIONS,
                                                                                    ),
                                                                                ),
                                                                                dbc.Row(
                                                                                    image_hovering,
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        className="border border-primary rounded mt-4",
                                                                    ),
                                                                    label="2D Visualization",
                                                                ),
                                                                dbc.Tab(
                                                                    dbc.Card(
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    viz_3d_row,
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        className="border border-primary rounded mt-4",
                                                                    ),
                                                                    label="3D Visualization",
                                                                ),
                                                                dbc.Tab(
                                                                    dbc.Card(
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    pca_loadings_row,
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        className="border border-primary rounded mt-4",
                                                                    ),
                                                                    label="PCA Statistics",
                                                                ),
                                                                dbc.Tab(
                                                                    dbc.Card(
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    pca_scatter_plot_row,
                                                                                    style={
                                                                                        "marginBottom": "50px",
                                                                                        "overflow": "auto",
                                                                                    },
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        className="border border-primary rounded mt-4",
                                                                    ),
                                                                    label="Age v. PC Statistics",
                                                                ),
                                                                dbc.Tab(
                                                                    dbc.Card(
                                                                        dbc.CardBody(
                                                                            [
                                                                                dbc.Row(
                                                                                    outliers_row,
                                                                                    style={
                                                                                        "marginBottom": "100px",
                                                                                        "overflow": "auto",
                                                                                    },
                                                                                ),
                                                                            ]
                                                                        ),
                                                                        className="border border-primary rounded mt-4",
                                                                    ),
                                                                    label="Outlier Detection",
                                                                ),
                                                            ],
                                                            style={
                                                                "marginTop": "24px",
                                                            },
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                width=10,
                            ),
                        ]
                    ),
                ],
                fluid=True,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("About"), close_button=False),
                    dbc.ModalBody(
                        "For more information, please visit the GitHub page."
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close-about", className="ms-auto", n_clicks=0
                        )
                    ),
                ],
                id="modal_about",
                is_open=False,
                keyboard=False,
                backdrop="static",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Contact"), close_button=False),
                    dbc.ModalBody("For any inquires, please check the GitHub page."),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close-contact", className="ms-auto", n_clicks=0
                        )
                    ),
                ],
                id="modal_contact",
                is_open=False,
                keyboard=False,
                backdrop="static",
            ),
        ],
        style={"overflow": "hidden"},
    )
    return content_layout
