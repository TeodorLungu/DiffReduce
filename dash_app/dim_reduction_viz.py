import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def create_explained_variance_plot(pca, pca_outlier):
    """
    Create a plot of the explained variance for PCA.
    """
    # Calculate the cumulative explained variance for PCA
    exp_var_cumul = np.cumsum(pca.explained_variance_ratio_)

    fig_pca = px.area(
        x=range(1, exp_var_cumul.shape[0] + 1),  # Number of components
        y=exp_var_cumul,
        labels={"x": "# Components", "y": "Explained Variance"},
    )

    """
    Create a plot of the explained variance for outlier PCA
    """
    # Calculate the cumulative explained variance for outlier PCA
    exp_var_cumul_outlier = np.cumsum(pca_outlier.explained_variance_ratio_)

    fig_outlier_pca = px.area(
        x=range(1, exp_var_cumul_outlier.shape[0] + 1),  # Number of components
        y=exp_var_cumul_outlier,
        labels={"x": "# Components", "y": "Explained Variance"},
    )

    return fig_pca, fig_outlier_pca


def stratified_sampling(dataframe, percentage, stratify_column="Bundle"):
    """
    Perform stratified sampling based on a given percentage.
    """
    if percentage <= 0 or percentage >= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    # Compute the sampling fraction
    fraction = percentage / 100.0

    # Perform stratified sampling
    stratified_df = (
        dataframe.groupby(stratify_column)
        .apply(lambda x: x.sample(frac=fraction, random_state=42))
        .reset_index(drop=True)
    )

    return stratified_df


def create_original_measures_plot(dataframe, measure_list, sampling_percentage=None):
    """
    Create a scatter matrix plot (SPLOM) and correlation heatmap for the original measures.
    Optionally apply stratified sampling based on the given percentage.
    """
    # Apply stratified sampling if a percentage is provided
    print(dataframe.columns)
    if sampling_percentage:
        dataframe_sampled = stratified_sampling(dataframe, sampling_percentage)
    else:
        dataframe_sampled = dataframe

    # Scatter matrix plot
    fig_scatter = px.scatter_matrix(
        dataframe_sampled,
        dimensions=measure_list,
        color="Bundle",
        opacity=0.6,  # Increase transparency
    )
    # Invisible diagonal
    fig_scatter.update_traces(diagonal_visible=False)
    # Margins
    fig_scatter.update_layout(
        yaxis_scaleanchor="x",
        margin=dict(b=50, t=50, l=50, r=50),
    )

    # Calculate correlation matrix
    corr_matrix = dataframe[measure_list].corr()
    print(corr_matrix)
    print(corr_matrix.columns, corr_matrix.index)

    # Create heatmap
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.index,
            y=corr_matrix.columns,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            hoverinfo="none",
            colorscale="Viridis",
            showscale=True,
        )
    )

    # Update heatmap layout
    fig_heatmap.update_layout(
        title="Correlation Heatmap",
        xaxis_title="Variables",
        yaxis_title="Variables",
        xaxis=dict(side="bottom"),
    )

    # Reverse y-axis, to match the scatter matrix
    fig_heatmap.update_yaxes(autorange="reversed")

    return fig_scatter, fig_heatmap


def create_loadings_line_plot(pca, measure_list, title="PCA Loadings"):
    """
    Create the PCA loadings plot
    """

    # Unit circle, for range
    fig = go.Figure(layout_yaxis_range=[-1.1, 1.1], layout_xaxis_range=[-1.1, 1.1])

    # Calculate the loadings
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    # Loop over each variable and draw a line from the origin
    for i, (pc1, pc2) in enumerate(loadings):
        fig.add_trace(
            go.Scatter(
                x=[0, pc1],
                y=[0, pc2],
                mode="lines+markers",
                name=measure_list[i],
            )
        )

    # Create a unit circle (loadings are normalized, always within the unit circle)
    theta = np.linspace(0, 2 * np.pi, 100)  # 100 points for a smooth circle
    x_circle = np.cos(theta)
    y_circle = np.sin(theta)

    # Add the unit circle to the plot
    fig.add_trace(
        go.Scatter(
            x=x_circle,
            y=y_circle,
            mode="lines",
            name="Unit Circle",
            showlegend=False,
            line=dict(dash="dash"),
        )
    )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis=dict(title="PC1", showgrid=True, zeroline=True),
        yaxis=dict(title="PC2", showgrid=True, zeroline=True),
        showlegend=True,
        yaxis_scaleanchor="x",
    )

    return fig


def create_pca_scatter_plot(
    dataframe,
    x="PC1",
    y="PC2",
    color="Bundle",
    hover_data=["Patient"],
    labels={"PC1": "Principal Component 1", "PC2": "Principal Component 2"},
    title="2D Scatter Plot with PCA",
):
    """
    Create PCA scatter plot, with the option to specify x, y, color, and hover data, labels, title

    Parameters:
    - dataframe (pd.DataFrame): Input DataFrame containing 'Patient', 'Bundle', and PCA components.
    - x (str): Column name for x-axis.
    - y (str): Column name for y-axis.
    - color (str): Column name for color.
    - hover_data (list): List of column names for hover data.
    - labels (dict): Dictionary specifying axis labels.
    - title (str): Title of the plot.
    """

    fig = px.scatter(
        dataframe,
        x=x,
        y=y,
        color=color,
        hover_data=hover_data,
        labels=labels,
        color_discrete_sequence=create_color_palette(),  # Use a custom color palette
        title=title,
    )

    return fig


def create_color_palette():
    """
    72 colors from plotly, for a more diverse color palette, for a maximum of 72 bundles
    plotly_colors = (
        px.colors.qualitative.Alphabet
        + px.colors.qualitative.Dark24
        + px.colors.qualitative.Light24
    )

    Custom color palette, for a maximum of 72 bundles
    Customly generated, to avoid color blindness issues, and to have a diverse color palette
    Keep previous code for reference, or to switch back to the default plotly color palette
    """

    plotly_colors = [
        "#5ff2ba",
        "#e60100",
        "#fdf401",
        "#034902",
        "#0a25fb",
        "#f8d3fe",
        "#8c8151",
        "#39f503",
        "#300978",
        "#d5e781",
        "#5c7fe6",
        "#0d7d70",
        "#ed25a1",
        "#621004",
        "#cb8f01",
        "#b08db2",
        "#029cea",
        "#13f46e",
        "#a0cdf6",
        "#6b6506",
        "#565a93",
        "#dc965f",
        "#bb23f6",
        "#15042a",
        "#7c1864",
        "#c1d130",
        "#454845",
        "#228925",
        "#0d5fb7",
        "#e8fec5",
        "#4ad8fe",
        "#0906bc",
        "#a68bfa",
        "#073456",
        "#53a0a8",
        "#dfbcb1",
        "#facf50",
        "#a2b66d",
        "#6612c3",
        "#1460fd",
        "#906f89",
        "#d91063",
        "#a1651e",
        "#53a647",
        "#9ec2bb",
        "#9ba416",
        "#f4ba1c",
        "#0c3590",
        "#343310",
        "#520a45",
        "#8b71ce",
        "#046641",
        "#39a877",
        "#d5f8f8",
        "#f2fe3c",
        "#3f68c0",
        "#785343",
        "#fcb584",
        "#5c1291",
        "#c9a8da",
        "#8ba196",
        "#03025b",
        "#fde09e",
        "#b88c3d",
        "#85a4df",
        "#395e6e",
        "#328af8",
        "#43b9d5",
        "#802233",
        "#696e68",
        "#0a1801",
        "#cbc85c",
    ]

    return plotly_colors
