import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import QuantileTransformer, StandardScaler


def run_pca_backend(df, n_components, normalize=True):
    """
    Runs Principal Component Analysis (PCA) on a DataFrame.

    Parameters:
    - df (DataFrame): The input DataFrame.
    - n_components (int): The number of components to keep.
    - normalize (bool): Whether to normalize the data or not. Default is True.

    Returns:
    - df_final (DataFrame): The DataFrame with PCA applied.
    """
    # Drop rows with NaN values
    df = df.dropna().reset_index(drop=True)

    # Encode categorical variable 'Bundle' with names
    df["Bundle"] = df["Bundle"].astype("category")
    bundle_categories = df["Bundle"].cat.categories  # Save the original categories
    df["Bundle"] = df["Bundle"].cat.codes
    # print(df.head())
    # Normalize the data if specified
    if normalize:
        features_to_normalize = df.drop(
            ["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"], axis=1
        )
        scaler = StandardScaler()
        df_normalized = scaler.fit_transform(features_to_normalize)
    else:
        df_normalized = df.drop(
            ["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"], axis=1
        )

    # Apply PCA
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(df_normalized)
    df_pca = pd.DataFrame(
        components, columns=[f"PC{i}" for i in range(1, n_components + 1)]
    )

    # Create a DataFrame for the reduced data
    df_final = pd.concat(
        [df[["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"]], df_pca],
        axis=1,
    )

    # Map back the original names to 'Bundle'
    df_final["Bundle"] = pd.Categorical.from_codes(
        df_final["Bundle"], categories=bundle_categories
    )

    return df_final, pca, components


def run_outlier_pca_backend(df):
    # Drop rows with NaN values
    df = df.dropna().reset_index(drop=True)

    # Encode categorical variable 'Bundle' with names
    df["Bundle"] = df["Bundle"].astype("category")
    bundle_categories = df["Bundle"].cat.categories  # Save the original categories
    df["Bundle"] = df["Bundle"].cat.codes
    # print(df.head())
    # Normalize the data if specified
    features_to_normalize = df.drop(
        ["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"], axis=1
    )
    scaler = QuantileTransformer(
        output_distribution="normal"
    )  # Use a quantile transformer with a normal distribution, which is robust to outliers
    # This is the only difference from the previous function
    df_normalized = scaler.fit_transform(features_to_normalize)

    # Apply PCA
    pca = PCA(n_components=0.95)  # Keep components that explain 95% of the variance
    components = pca.fit_transform(df_normalized)

    # Get the explained variance ratio for each component
    explained_variance_ratio = pca.explained_variance_ratio_

    # Calculate the cumulative explained variance
    cumulative_explained_variance = np.cumsum(explained_variance_ratio)

    # Determine the number of components that explain a certain threshold of variance
    threshold = 0.95  # Threshold of 95% variance
    n_components = (
        np.argmax(cumulative_explained_variance >= threshold) + 1
    )  # Number of components that explain the threshold

    df_pca = pd.DataFrame(
        components, columns=[f"PC{i}" for i in range(1, n_components + 1)]
    )
    print(df_pca)

    # Create a DataFrame for the reduced data
    df_final = pd.concat(
        [df[["Patient", "Patient_ID", "Bundle", "Sex", "Age", "Age_Group"]], df_pca],
        axis=1,
    )

    # Map back the original names to 'Bundle'
    df_final["Bundle"] = pd.Categorical.from_codes(
        df_final["Bundle"], categories=bundle_categories
    )

    return df_final, pca, components
