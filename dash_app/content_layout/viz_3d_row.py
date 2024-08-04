import random

import dash_bootstrap_components as dbc
import dash_vtk
from dash import html

viz_3d_row = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H5(
                    "3D Tract Viewer",
                    className="text-center mt-2",
                ),
                width={
                    "size": 6,
                    "offset": 3,
                },
            ),
        ),
        dbc.Row(
            html.Div(
                children=[
                    dash_vtk.View(
                        id="vtk-view",
                        triggerResetCamera=random.random(),
                        # background=[234/255, 226/255, 226/255],
                        background=[
                            1,
                            1,
                            1,
                        ],
                        children=[
                            dash_vtk.VolumeRepresentation(
                                children=[
                                    dash_vtk.VolumeController(),
                                    dash_vtk.Volume(id="vtk-volume"),
                                ],
                            ),
                            dash_vtk.GeometryRepresentation(
                                children=[
                                    dash_vtk.Mesh(
                                        id="vtk-mesh",
                                    ),
                                ],
                                property={
                                    "ambient": 0.1,
                                    "diffuse": 1.0,
                                    "specular": 0.5,
                                    "specularPower": 20,
                                },
                            ),
                        ],
                    ),
                ],
                style={
                    "height": "600px",
                },
            ),
        ),
    ],
    id="vtk-html-view",
)
