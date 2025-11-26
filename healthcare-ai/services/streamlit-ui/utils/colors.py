"""
Color utility functions for HealthGuide AI
"""

COLOR_PALETTE = {
    "steel_blue": "#6F9BAF",
    "alice_blue": "#ECF4F7", 
    "blue_slate": "#576770",
    "pearl_aqua": "#88C4C9",
    "platinum": "#E6EAEF"
}

GRADIENTS = {
    "primary": "linear-gradient(135deg, #6F9BAF, #88C4C9)",
    "light": "linear-gradient(135deg, #ECF4F7, #E6EAEF)",
    "dark": "linear-gradient(135deg, #576770, #6F9BAF)"
}

def get_gradient(gradient_name):
    return GRADIENTS.get(gradient_name, GRADIENTS["primary"])

def get_color(color_name):
    return COLOR_PALETTE.get(color_name, "#6F9BAF")