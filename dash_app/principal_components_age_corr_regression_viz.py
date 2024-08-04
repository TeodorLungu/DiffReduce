import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from patsy import dmatrix
from sklearn.metrics import r2_score

import auxiliary_functions


class SplineRegression:
    # Class for Splines Regression
    def __init__(
        self,
        dataframe,
        response_var,
        predictor_var,
        bundle_var,
        degree=3,
        knots=None,
        method="GLM",
        by_variable=None,
        plots=None,
    ):
        self.df = dataframe
        self.response_var = response_var
        self.predictor_var = predictor_var
        self.bundle_var = bundle_var
        self.degree = degree
        self.knots = knots
        self.method = method
        self.by_variable = by_variable
        self.models = None
        self.plots = plots

    def fit_model(self):
        # Fit the model
        self._set_knots()  # Set the knots if not specified
        if self.by_variable:
            self._fit_models_by_variable()  # Fit models by variable, that is if there is a by_variable, split the data by the variable and fit a model for each level
        else:
            print(
                "Single Model"
            )  # Fit a single model, that is if there is no by_variable, fit a single model to the entire data
            self._fit_single_model()
        return self.models

    def _set_knots(self):
        # Set the knots if not specified, to the 25th, 50th, and 75th percentiles
        if self.knots is None:
            self.knots = np.percentile(self.df[self.predictor_var], [25, 50, 75])

    def _fit_models_by_variable(self):
        # Fit models by variable
        self.models = {}  # Initialize an empty dictionary to store the models
        for level in self.df[
            self.by_variable
        ].unique():  # Iterate over the unique levels of the by_variable
            sub_df = self.df[
                self.df[self.by_variable] == level
            ]  # Subset the data by the level of the by_variable
            self.models[level] = self._fit_model(
                sub_df
            )  # Fit a model to the subset of data

    def _fit_single_model(self):
        self.models = {
            "Overall": self._fit_model(self.df)
        }  # Fit a single model to the entire data

    def _fit_model(self, data):
        design_matrix = dmatrix(  # Create a design matrix for the spline regression, using the predictor variable, knots, and degree
            f"bs({self.predictor_var}, knots={tuple(self.knots)}, degree={self.degree}, include_intercept=False)",
            data,
            return_type="dataframe",
        )
        response_var = data[self.response_var]
        if self.method == "GLM":
            model = sm.GLM(
                response_var, design_matrix
            ).fit()  # Fit a Generalized Linear Model (GLM) to the data
        return model

    def calculate_diagnostics(self):
        # Calculate diagnostics for the models
        r2 = {}
        p_values = {}
        for level, model in self.models.items():  # Iterate over the models
            if self.by_variable:
                data_subset = self.df[
                    self.df[self.by_variable] == level
                ]  # Subset the data by the level of the by_variable
            else:
                data_subset = self.df  # Use the entire data if there is no by_variable
            r2[level] = r2_score(
                data_subset[self.response_var], model.predict()
            )  # Calculate the R-squared value for the model
            p_values[level] = model.pvalues  # Get the p-values for the model
        return {"R2": r2, "p-values": p_values}

    def fit_model_to_df(self):
        # Used in app_integrated_data.py, to return the model output tables to a dictionary, to be written to an Excel file
        models_outputs_dict = {}
        for i, model in self.models.items():
            tables = model.summary2()  # Get the summary of the model
            table_1 = tables.tables[0]  # Get the first table from the summary
            table_2 = tables.tables[1]  # Get the second table
            models_outputs_dict[i] = {
                "table_1": table_1,
                "table_2": table_2,
            }  # Store the tables in a dictionary
        return models_outputs_dict

    def plot(self, color_column=None, hover_data=None):
        figs = []
        combined_fig = None
        # Add spline fit line for each model
        for level, model in self.models.items():
            title = f"{self.response_var} vs {self.predictor_var} with Spline Regression using {self.method} method for bundle {self.bundle_var}"
            if self.by_variable:  # Add the level of the by_variable to the title
                title += f" for {self.by_variable} = {auxiliary_functions.get_sex_label(level)}"
            title += f" (R2 = {self.calculate_diagnostics()['R2'][level]:.2f})"  # Add the R-squared value to the title
            # Subset the data by the level of the by_variable
            if self.by_variable:
                df_subset = self.df[self.df[self.by_variable] == level]
            else:
                df_subset = self.df  # Use the entire data if there is no by_variable

            # Create scatter plot
            fig_pca = px.scatter(
                df_subset,
                x=self.predictor_var,
                y=self.response_var,
                color=color_column if color_column else None,
                hover_data=hover_data,
                title=title,
            )

            # Create spline fit line
            x_range = np.linspace(
                self.df[self.predictor_var].min(),
                self.df[self.predictor_var].max(),
                500,
            )

            # Create a design matrix for the spline regression
            x_range_spline = dmatrix(
                f"bs(x_range, knots={tuple(self.knots)}, degree={self.degree}, include_intercept=False)",
                {"x_range": x_range},
                return_type="dataframe",
            )

            # Predict the response variable using the model
            y_range_spline = model.predict(x_range_spline)
            ci_lower, ci_upper = model.get_prediction(x_range_spline).conf_int().T

            # Add a name to the spline fit line, based on the by_variable (if present)
            spline_name = (
                f"{self.method} Spline Fit"
                if not self.by_variable
                else f"{self.method} Spline Fit ({auxiliary_functions.get_sex_label(level)})"
            )
            # Add spline fit line
            fig_pca.add_scatter(
                x=x_range,
                y=y_range_spline,
                mode="lines",
                name=spline_name,
            )

            # add confidence interval name, based on the by_variable (if present)
            confidence_interval_name = (
                f"{self.method} Spline Fit Confidence Interval"
                if not self.by_variable
                else f"{self.method} Spline Fit Confidence Interval ({auxiliary_functions.get_sex_label(level)})"
            )
            # Add confidence interval
            fig_pca.add_scatter(
                x=np.concatenate([x_range, x_range[::-1]]),
                y=np.concatenate([ci_lower, ci_upper[::-1]]),
                fill="toself",
                fillcolor="rgba(0,100,80,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name=confidence_interval_name,
            )

            # Customize layout
            fig_pca.update_layout(
                xaxis_title=self.predictor_var,
                yaxis_title=self.response_var,
                legend_title="Legend",
                height=600,
            )

            # Move legend to the left if 'Age' is the color variable
            if color_column == "Age":
                fig_pca.update_layout(
                    legend=dict(x=0, y=1, traceorder="normal", orientation="v")
                )
            if self.plots == "Different Plot" or self.plots is None:
                figs.append(fig_pca)  # Append the figure to the list of figures
            elif self.plots == "Same Plot":
                if (
                    combined_fig is None
                ):  # Create combined figure if not created yet, and add the data
                    combined_fig = fig_pca
                else:
                    for data in fig_pca.data:
                        combined_fig.add_trace(data)

        # Append combined figure if it exists
        if combined_fig is not None:
            R2_scores = []
            for level, _ in self.models.items():
                R2_scores.append(self.calculate_diagnostics()["R2"][level])
            combined_fig.update_layout(
                title_text=f"{self.response_var} vs {self.predictor_var} with Spline Regression using {self.method} method for bundle {self.bundle_var} for Female (R2 = {R2_scores[0]:.2f})/Male (R2 = {R2_scores[1]:.2f})",
            )
            figs.append(combined_fig)

        return figs
