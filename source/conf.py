# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TKF\'s Notes'
copyright = '2022, Kaifu Tian'
author = 'Kaifu Tian'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_comments"
]

comments_config = {
    "utterances": {
        "repo": "rcore-os/rCore-Tutorial-Book-v3",
        "issue-term": "pathname",
        "label": "comments",
        "theme": "github-light",
        "crossorigin": "anonymous",
    }
}

templates_path = ['_templates']
exclude_patterns = []

language = 'zh_CN'
html_search_language = 'zh'

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
html_title = "Notes"

pygments_style = "sphinx"
pygments_dark_style = "monokai"
