import plotly.express as px
import logging
import numpy as np
import uuid
import hashlib

logger = logging.getLogger(__name__)

def create_histogram_figure(DF, column_name):
    """
    Creates a histogram figure for a specific column in the dataframe.

    Args:
        DF (pd.DataFrame): The dataframe containing the data.
        column_name (str): The name of the column to plot.

    Returns:
        plotly.graph_objs.Figure: The histogram figure.
    """
    dataset_size = len(DF)
    numbins = min(dataset_size // 10, 1000)
    fig = px.histogram(DF, x=column_name, nbins=numbins)
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        height=100,
        margin=dict(t=10, l=10, r=10, b=10),
        xaxis=dict(
            title=column_name,
            title_font=dict(size=14),
        ),
    )
    return fig

def generate_plot(
    df_filtered, x_column_name, y_column_name, cluster_column_name, selected_categories, plot_marginals='violin'
):
    """
    Generates the main scatter plot based on filtered data.

    Args:
        df_filtered (pd.DataFrame): The filtered dataframe.
        x_column_name (str): Column name for X axis.
        y_column_name (str): Column name for Y axis.
        cluster_column_name (str): Column name for color/cluster.
        selected_categories (list): List of selected categories for ordering.
        plot_marginals (str, optional): Type of marginal plot ('violin' or 'histogram'). Defaults to 'violin'.

    Returns:
        plotly.graph_objs.Figure: The scatter plot figure.
    """
    # Print the dtype of the columns:
    logging.info(
        f"X: {df_filtered[x_column_name].dtype}, Y: {df_filtered[y_column_name].dtype}, Cluster: {df_filtered[cluster_column_name].dtype}, Selected Categories: {selected_categories}"
    )

    plot_type = "scatter"

    if plot_type == "scatter":
        fig = px.scatter(
            df_filtered,
            x=x_column_name,
            y=y_column_name,
            color=cluster_column_name,
            category_orders={cluster_column_name: selected_categories},
            custom_data=["id"],
            marginal_x=plot_marginals,
            marginal_y=plot_marginals,

        )
        fig.update_layout(
            hovermode="closest",
            height=800,
            clickmode="event+select",
        )

    return fig

def prinfo(message):
    """Logs an info message."""
    logger.info(message)
    
def prerror(message):
    """Logs an error message."""
    logger.error(message)

def prdebug(message):
    """Logs a debug message."""
    logger.debug(message)
    
def prwarn(message):
    """Logs a warning message."""
    logger.warning(message)
    
def harmonize_image(image_to_display):
    """
    Harmonizes image contrast by clipping values based on mean and std deviation.

    Args:
        image_to_display (np.array): The image array.

    Returns:
        np.array: The harmonized image array.
    """
    mean = np.mean(image_to_display)
    std = np.std(image_to_display)
    lower_bound = mean - 3*std
    if lower_bound < 0:
        lower_bound = 0
    image_to_display = np.clip(image_to_display, lower_bound, mean+3*std)
    return image_to_display

def generate_token():
    """
    Generates a unique token based on the machine's MAC address.

    Returns:
        str: A short hash token.
    """
    # Get the MAC address of the machine
    mac = uuid.getnode()
    
    # Hash the MAC address using SHA256
    mac_hash = hashlib.sha256(str(mac).encode()).hexdigest()
    
    # Use a part of the hash as the token
    token = mac_hash[:8]
    
    return token

def sort_categories(DF, selected_column, df_filtered=None):
    """
    Sorts categories numerically if possible, otherwise alphabetically.

    Args:
        DF (pd.DataFrame): The original dataframe.
        selected_column (str): The column to sort.
        df_filtered (pd.DataFrame, optional): Filtered dataframe. Defaults to None.

    Returns:
        np.array: Sorted unique categories.
    """
    if df_filtered is None:
        df_filtered = DF

    def convert_to_numeric(category_str):
        try:
            return float(category_str)
        except ValueError:
            return category_str

    logging.info(df_filtered.shape)
    all_categories = df_filtered[selected_column].unique()
    logging.info(f"Categories: {all_categories}")
    categories_as_numbers = [convert_to_numeric(cat) for cat in all_categories]
    sorted_indices = np.argsort(categories_as_numbers)
    logging.info(f"Sorted Categories: {all_categories[sorted_indices]}")
    return all_categories[sorted_indices]
