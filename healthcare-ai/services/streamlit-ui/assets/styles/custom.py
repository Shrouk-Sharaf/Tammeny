import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
    <style>
        /* Import the main CSS file */
    </style>
    """, unsafe_allow_html=True)

def get_color_palette():
    """Return consistent color palette for charts"""
    return {
        'primary': '#3498db',
        'secondary': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'dark': '#2c3e50',
        'light': '#ecf0f1'
    }