import os

import dash_bootstrap_components as dbc
from dotenv import load_dotenv

load_dotenv()  # Take environment variables from .env file

# Theme for the Dash app
DBC_CSS = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
DBC_THEME = dbc.themes.SANDSTONE

# The following are the default values for the dropdowns in the patient selector
DEFAULT_BUNDLES = ["AF_left", "CC"]
DEFAULT_MEASURES = [
    "FA",
    "wm_volume",
    "MD",
]
DEFAULT_AGE_GROUPS = [1, 2, 3, 4]
DEFAULT_SEXES = [70, 77]

# Base directory for the data (3D images, screenshots)
BASE_DIR_FALLBACK = os.getenv("BASE_DIR_FALLBACK")
BASE_DIR_FULL = os.getenv("BASE_DIR_FULL")

# Mapping for the axis values
MAPPING_DICT = {
    "Axial Inferior": "axial_inferior",
    "Axial Superior": "axial_superior",
    "Coronal Anterior": "coronal_anterior",
    "Coronal Posterior": "coronal_posterior",
    "Sagittal Left": "sagittal_left",
    "Sagittal Right": "sagittal_right",
}

# Path to the logo
LOGO = "./content_layout/logo.png"

# Options for the image download
IMAGE_DOWNLOAD_OPTIONS = {
    "toImageButtonOptions": {
        "format": "svg",  # one of png, svg, jpeg, webp
        "filename": "custom_image",
        "height": 500,
        "width": 700,
        "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
    }
}
