
class AppState:
    def __init__(self):
        self.DF = None
        self.selected_categorical_options = []
        self.selected_numeric_options = []
        self.ROOT_DIR = ""
        self.HARMONIZE = False
        self.selected_rows_global = []
        self.TOKEN = ""
        self.PORT = 8050
        self.PLOT_MARGINALS = 'violin'
        self.DEBUG = False

state = AppState()
