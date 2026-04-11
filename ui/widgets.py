import tkinter as tk
from tkinter import ttk

class SearchableCombobox(ttk.Combobox):
    def __init__(self, master, **kwargs):
        # Force state to normal so users can type for search functionality
        kwargs["state"] = "normal"
        super().__init__(master, **kwargs)
        self._all_values = []
        # KeyRelease allows us to react after the character has entered the widget buffer
        self.bind('<KeyRelease>', self._handle_keyrelease)
        
    # Replaces default assignment directly to self['values']
    def set_values(self, values):
        self._all_values = values
        self['values'] = values
        
    def _handle_keyrelease(self, event):
        # Ignore navigation and control keys
        nav_keys = (
            "Up", "Down", "Left", "Right", "Return", "Escape", 
            "Shift_L", "Shift_R", "Control_L", "Control_R", 
            "Alt_L", "Alt_R", "Tab"
        )
        if event.keysym in nav_keys:
            return
            
        typed = self.get().lower()
        if typed == '':
            self['values'] = self._all_values
        else:
            filtered = [v for v in self._all_values if typed in v.lower()]
            self['values'] = filtered
