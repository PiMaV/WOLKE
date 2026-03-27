import logging
import plotly.express as px
import plotly.graph_objects as go

class PlotGenerator:
    """
    A class to generate scatter plots (2D or 3D) using Plotly Graph Objects.
    """

    def generate_plot(
        self,
        df_filtered,
        x_column_name,
        y_column_name,
        cluster_column_name,
        selected_categories,
        z_column_name=None,
        marginal_x=None,
        marginal_y=None
    ):
        """
        Generates a scatter plot (2D or 3D) based on the input parameters.
        
        The plot type is determined by whether `z_column_name` is provided:
            - If None, a 2D scatter plot is generated.
            - If provided, a 3D scatter plot is generated.
        
        Logs the data types of key columns and creates a Plotly figure.
        
        Args:
            df_filtered (DataFrame): The filtered DataFrame containing the data.
            x_column_name (str): Column name for the x-axis.
            y_column_name (str): Column name for the y-axis.
            cluster_column_name (str): Column name used for coloring/grouping.
            selected_categories (list): Order of categories for the cluster.
            z_column_name (str, optional): Column name for the z-axis. If provided, a 3D scatter plot is generated.
            marginal_x (str, optional): Type of marginal plot for the x-axis.
            marginal_y (str, optional): Type of marginal plot for the y-axis.
        
        Returns:
            plotly.graph_objects.Figure: The generated Plotly figure.
        """
        def _empty_fig(title: str):
            return go.Figure(data=[go.Scatter(x=[], y=[], mode="markers")]).update_layout(
                height=800,
                title=title,
            )

        if df_filtered is None or len(df_filtered) == 0:
            return _empty_fig("Keine Daten nach Filter – Subset/Filter anpassen oder Spalten pruefen.")
        for col in (x_column_name, y_column_name, cluster_column_name):
            if col not in df_filtered.columns:
                logging.warning("Plot: Spalte '%s' fehlt im DataFrame. Verfuegbare: %s", col, list(df_filtered.columns))
                return _empty_fig(f"Spalte '{col}' fehlt. Achsen-Dropdowns pruefen (Config: x/y/color).")
        logging.info(
            f"X: {df_filtered[x_column_name].dtype}, "
            f"Y: {df_filtered[y_column_name].dtype}, "
            f"Cluster: {df_filtered[cluster_column_name].dtype}, "
            f"Selected Categories: {selected_categories}"
        )
        cat_order = list(selected_categories) if selected_categories is not None and len(selected_categories) > 0 else None
        if hasattr(cat_order, "__iter__") and not isinstance(cat_order, (list, tuple)):
            cat_order = list(cat_order)

        # Convert unsupported marginal options (like "off") to None
        if marginal_x == "off":
            marginal_x = None
        if marginal_y == "off":
            marginal_y = None

        scatter_kw = dict(
            x=x_column_name,
            y=y_column_name,
            color=cluster_column_name,
        )
        if "id" in df_filtered.columns:
            scatter_kw["custom_data"] = ["id"]
        if cat_order:
            scatter_kw["category_orders"] = {cluster_column_name: cat_order}
        if z_column_name is None:
            scatter_kw["marginal_x"] = marginal_x
            scatter_kw["marginal_y"] = marginal_y
            fig = px.scatter(df_filtered, **scatter_kw)
            fig.update_layout(
                hovermode="closest",
                height=800,
                clickmode="event+select",
            )
        else:
            scatter_3d_kw = dict(
                x=x_column_name,
                y=y_column_name,
                z=z_column_name,
                color=cluster_column_name,
                **(dict(category_orders={cluster_column_name: cat_order}) if cat_order else {}),
            )
            if "id" in df_filtered.columns:
                scatter_3d_kw["custom_data"] = ["id"]
            fig = px.scatter_3d(df_filtered, **scatter_3d_kw)
            fig.update_layout(
                hovermode="closest",
                height=800,
                clickmode="event+select",
            )

        return fig
