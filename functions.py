import plotly.express as px
import logging
import numpy as np
import uuid
import hashlib

logger = logging.getLogger(__name__)

def create_histogram_figure(DF, column_name):
    dataset_size = len(DF)
    numbins = min(dataset_size // 10, 1000)
    fig = px.histogram(DF, x=column_name, nbins=numbins)
    fig.update_traces(opacity=0.6)  # Set the opacity of the bars
    fig.update_layout(
        height=100,  # Make the plot smaller in height
        margin=dict(t=10, l=10, r=10, b=10),  # Tighten the margins around the plot
        xaxis=dict(
            title=column_name,  # X-axis label
            title_font=dict(size=14),  # Make the x-axis labels bigger
        ),
    )
    return fig

def prinfo(message):
    logger.info(message)
    
def prerror(message):
    logger.error(message)

def prdebug(message):
    logger.debug(message)
    
def prwarn(message):
    logger.warning(message)
    
def harmonize_image(image_to_display):
    mean = np.mean(image_to_display)
    std = np.std(image_to_display)
    lower_bound = mean - 3*std
    if lower_bound < 0:
        lower_bound = 0
    image_to_display = np.clip(image_to_display, lower_bound, mean+3*std)
    return image_to_display

def generate_token():
    # Get the MAC address of the machine
    mac = uuid.getnode()
    
    # Hash the MAC address using SHA256 (or another algorithm of your choice)
    mac_hash = hashlib.sha256(str(mac).encode()).hexdigest()
    
    # Use a part of the hash as the token (e.g., first 8 characters)
    token = mac_hash[:8]
    
    return token

def sort_categories(DF, selected_column, df_filtered=None):
    if df_filtered is None:
        df_filtered = DF

    def convert_to_numeric(category_str):
        try:
            return float(category_str)  # Try converting to a number
        except ValueError:
            return category_str  # Treat as a non-numeric string

    logging.info(df_filtered.shape)
    all_categories = df_filtered[selected_column].unique()
    logging.info(f"Categories: {all_categories}")
    categories_as_numbers = [convert_to_numeric(cat) for cat in all_categories]
    # sort numerically if possible, otherwise alphabetically
    sorted_indices = np.argsort(categories_as_numbers)
    logging.info(f"Sorted Categories: {all_categories[sorted_indices]}")
    return all_categories[sorted_indices]