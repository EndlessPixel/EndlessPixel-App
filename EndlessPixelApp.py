#!/usr/bin/python3
import pathlib
import tkinter as tk
import tkinter.ttk as ttk
import pygubu
from EndlessPixelAppui import EndlessPixelAppUI

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "EP.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class EndlessPixelApp(EndlessPixelAppUI):
    def __init__(self, master=None):
        super().__init__(
            master,
            project_ui=PROJECT_UI,
            resource_paths=RESOURCE_PATHS,
            translator=None,
            on_first_object_cb=None
        )
        self.builder.connect_callbacks(self)

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = EndlessPixelApp()
    app.run()
