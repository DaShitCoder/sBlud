import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "firebase_auth",
    path=os.path.dirname(os.path.abspath(__file__))
)

def firebase_auth_button(key=None):
    return _component_func(key=key, default=None)
