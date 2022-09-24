# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TKF\'s Daily Notes'
copyright = '2022, TKF'
author = 'TKF'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'zh'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_theme_options = {
    "sidebar_hide_name": True,

    # Adding an edit button
    "source_repository": "https://github.com/tkf2019/Blog",
    "source_branch": "main",
    "source_directory": "source/",

    # Changing Furo's blue accent
    "light_css_variables": {
        "color-brand-primary": "#7C4DFF",
        "color-brand-content": "#7C4DFF",
    },

}

# Custom options for Furo

# html_logo = '_static/logo.jpeg'
html_title = "Daily Notes"

pygments_style = "sphinx"
pygments_dark_style = "monokai"
