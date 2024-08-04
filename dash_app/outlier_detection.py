import numpy as np
import pandas as pd
from sklearn.covariance import MinCovDet
from sklearn.svm import OneClassSVM


def calculate_parameters_mcd(data):
    """
    Calculate the mean vector and inverse covariance matrix using Minimum Covariance Determinant (MCD).
    """
    mcd = MinCovDet().fit(data)
    mean_vector = mcd.location_
    covariance_matrix = mcd.covariance_

    try:
        inv_covariance_matrix = np.linalg.inv(
            covariance_matrix
        )  # Calculate the inverse of the covariance matrix
    except np.linalg.LinAlgError:
        print(
            "Warning: Covariance matrix is singular. Using pseudoinverse instead."
        )  # Handle singular covariance matrix
        inv_covariance_matrix = np.linalg.pinv(
            covariance_matrix
        )  # Calculate the pseudoinverse of the covariance matrix

    return mean_vector, inv_covariance_matrix


def MahalanobisDist(x, mean_vec, inv_covmat):
    """
    Compute the Mahalanobis distance between a data point and the mean vector.
    """
    diff = (
        x - mean_vec
    )  # Calculate the difference between the data point and the mean vector
    md = np.sqrt(
        np.dot(np.dot(diff, inv_covmat), diff.T)
    )  # Calculate the Mahalanobis distance
    return md


def determine_threshold(md, alpha=0.01):
    """
    Determine the threshold for the Mahalanobis distance based on the desired alpha level.
    This percentile is used to identify outliers in the data.
    """
    threshold = np.percentile(md, 100 * (1 - alpha))
    return threshold


def detect_outliers(data, mean_vec, inv_covmat, threshold):
    """
    Detect outliers in the data based on the Mahalanobis distance and the threshold.
    """
    # Calculate the Mahalanobis distance for each data point
    m_distances = np.array([MahalanobisDist(x, mean_vec, inv_covmat) for x in data])
    # Determine the outliers based on the threshold
    outliers = m_distances > threshold
    return outliers


def pca_truncate_for_anomaly_detector(pca_df, bundle=None, age_group=None):
    """
    Perform truncation of the PCA DataFrame based on the specified bundle and age group.
    """
    if bundle is not None:  # Check if a bundle is specified
        pca_df = pca_df[pca_df["Bundle"] == bundle]

    if age_group is not None:  # Check if an age group is specified
        pca_df = pca_df[pca_df["Age_Group"] == age_group]
    return pca_df


def anomaly_detector_caller(pca_df, q, alpha=0.01, nu=0.1):
    """
    Entry function to call the anomaly detector, which combines Mahalanobis distance and OCSVM.
    """

    # List of principal components
    pc_list = [f"PC{i}" for i in range(1, q + 1)]
    # Calculate parameters from the full data
    pca_array = pca_df[pc_list].values
    mean_vector, inv_covariance_matrix = calculate_parameters_mcd(pca_array)
    # Calculate Mahalanobis distances and determine the threshold
    md = np.array(
        [MahalanobisDist(x, mean_vector, inv_covariance_matrix) for x in pca_array]
    )
    threshold = determine_threshold(md, alpha=alpha)
    # Detect outliers in the data using the Mahalanobis distance
    test_outliers = detect_outliers(
        pca_array, mean_vector, inv_covariance_matrix, threshold
    )

    # Remove the Mahalanobis outliers from the data
    non_outliers = pca_df[~test_outliers]

    # Train OCSVM on the data without the Mahalanobis outliers
    ocsvm = OneClassSVM(kernel="rbf", nu=nu)  # RBF kernel with nu hyperparameter
    ocsvm.fit(
        non_outliers[pc_list]
    )  # Fit the OCSVM on the non-outliers, using the principal components

    # Predict outliers using the OCSVM
    ocsvm_outliers = (
        ocsvm.predict(pca_df[pc_list]) == -1
    )  # Predict outliers using the OCSVM
    outlier_indices = np.where(ocsvm_outliers)[0]  # Get the indices of the outliers
    # Extract the outliers from the PCA DataFrame
    outlier_df = pca_df.iloc[outlier_indices]

    return outlier_df
