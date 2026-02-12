from datetime import datetime

project = "Homepage"
author = "Kaifu Tian"
copyright = f"{datetime.now():%Y}, {author}"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
root_doc = "index"

language = "en"

html_theme = "pydata_sphinx_theme"
html_title = "TKF"
html_static_path = ["_static"]
html_extra_path = ["images"]
html_css_files = ["custom.css"]

html_theme_options = {
    "navigation_with_keys": True,
    "show_toc_level": 2,
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "secondary_sidebar_items": ["page-toc"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/tkf2019",
            "icon": "fa-brands fa-github",
        }
    ],
}

html_context = {
    "default_mode": "light",
}
