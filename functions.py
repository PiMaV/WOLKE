import plotly.express as px
import logging
import numpy as np

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
    
def harmonize_image(image_to_display):
    mean = np.mean(image_to_display)
    std = np.std(image_to_display)
    lower_bound = mean - 3*std
    if lower_bound < 0:
        lower_bound = 0
    image_to_display = np.clip(image_to_display, lower_bound, mean+3*std)
    return image_to_display