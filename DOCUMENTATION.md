# WOLKE - Web-Oriented Layout for Knowledge Exploration

WOLKE is a Dash-based web application designed for exploring and visualizing complex datasets, particularly focused on image analysis data. It allows users to filter, subsample, and visualize data points using interactive scatter plots and histograms, and to view associated images.

## Features

- **Interactive Scatter Plot**: Visualize high-dimensional data using X, Y, and Color dimensions.
- **Marginal Plots**: View distributions of X and Y axes using histograms or violin plots.
- **Data Filtering**: Filter data by categorical values and numeric ranges.
- **Image Visualization**: Click on data points to view associated images (supports `.npy` files).
- **Subsampling**: Work with a subset of data for performance and then apply filters to the full dataset.
- **Dataset Download**: Download the filtered dataset or specific image files.

## Project Structure

The project is organized into modular components:

- **`app.py`**: The main entry point. Initializes the Dash app, server, and socketio. It sets up the layout and registers callbacks.
- **`callbacks.py`**: Contains all Dash callbacks.
    - `register_numeric_callbacks`: Handles histogram updates and range limits.
    - `register_categorical_callbacks`: Handles categorical dropdowns and filtering logic.
    - `register_plot_callbacks`: Core logic for updating the main scatter plot based on all filters (numeric, categorical, subsampling).
    - `register_image_callbacks`: Handles image loading and display.
    - `register_collapse_button_callbacks`: Manages the UI collapse sections.
- **`layout.py`**: Defines the visual layout of the application using Dash Bootstrap Components.
- **`data_loader.py`**: Handles loading data from SQLite databases (`.db` files). It identifies the largest table and loads it into a Pandas DataFrame.
- **`functions.py`**: Utility functions for plotting (`generate_plot`, `create_histogram_figure`), image processing (`harmonize_image`), and other helpers.
- **`state.py`**: Manages shared application state (e.g., loaded DataFrame, configuration, global selections) to avoid circular imports and manage global variables cleanly.
- **`config.ini`**: Configuration file for default settings.

## Setup and Installation

1.  **Clone the repository**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure `dash_mantine_components==0.12.1` is installed as per requirements.*

3.  **Prepare Data**:
    - Place your SQLite database (`.db`) file in a folder.
    - The database should contain a table with columns including `relative_filepath` (for images) and `id`.
    - Images (if using `.npy` format) should be relative to the root folder.

4.  **Configuration**:
    - Edit `config.ini` to set the `root_dir` pointing to your data folder.
    - You can also configure default plot axes and port.

## Running the Application

Run the application using Python:

```bash
python app.py
```

Open your web browser and navigate to `http://localhost:8050` (or the port specified in config).

## Configuration (`config.ini`)

```ini
[settings]
root_dir = /path/to/your/data
debug = False
port = 8050
plot_marginals = violin  # Options: 'violin', 'histogram'

[image_plot]
x = mean
y = std
color = sharpness
```

## Usage

1.  **Subset**: Adjust the slider to work with a smaller sample for faster initial exploration.
2.  **Categories**: Select or deselect categorical values to filter the data.
3.  **Histograms**: Drag on the histograms or enter values to filter by numeric ranges.
4.  **Axes**: Choose which columns to display on X, Y, and Color axes.
5.  **Explore**:
    - Interact with the scatter plot (zoom, pan).
    - Click a point to load its image below the plot.
    - Use Box/Lasso select to filter the data table below.
