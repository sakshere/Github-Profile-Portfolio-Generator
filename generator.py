"""
Portfolio Site Generator
Renders the portfolio template with GitHub data and packages it as a downloadable ZIP.
"""

import os
import shutil
import uuid
import zipfile
from jinja2 import Environment, FileSystemLoader
from github_api import get_language_color


# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
PORTFOLIO_ASSETS_DIR = os.path.join(TEMPLATES_DIR, "portfolio", "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


# Available themes
THEMES = {
    "dark": {
        "name": "Midnight Dark",
        "bg_primary": "#0a0a0f",
        "bg_secondary": "#12121a",
        "bg_card": "#1a1a2e",
        "text_primary": "#e0e0e0",
        "text_secondary": "#a0a0b0",
        "accent": "#7c3aed",
        "accent_hover": "#8b5cf6",
        "accent_glow": "rgba(124, 58, 237, 0.3)",
        "gradient_start": "#7c3aed",
        "gradient_end": "#2563eb",
        "border": "rgba(255, 255, 255, 0.06)",
    },
    "ocean": {
        "name": "Ocean Blue",
        "bg_primary": "#0a192f",
        "bg_secondary": "#112240",
        "bg_card": "#1d3461",
        "text_primary": "#ccd6f6",
        "text_secondary": "#8892b0",
        "accent": "#64ffda",
        "accent_hover": "#80ffea",
        "accent_glow": "rgba(100, 255, 218, 0.2)",
        "gradient_start": "#64ffda",
        "gradient_end": "#48b1bf",
        "border": "rgba(100, 255, 218, 0.1)",
    },
    "sunset": {
        "name": "Sunset Glow",
        "bg_primary": "#1a0a2e",
        "bg_secondary": "#16213e",
        "bg_card": "#2a1a4e",
        "text_primary": "#f0e6ff",
        "text_secondary": "#b8a9d4",
        "accent": "#ff6b6b",
        "accent_hover": "#ff8787",
        "accent_glow": "rgba(255, 107, 107, 0.25)",
        "gradient_start": "#ff6b6b",
        "gradient_end": "#ffa726",
        "border": "rgba(255, 107, 107, 0.1)",
    },
    "forest": {
        "name": "Forest Green",
        "bg_primary": "#0a1a0a",
        "bg_secondary": "#0f2a0f",
        "bg_card": "#1a3a1a",
        "text_primary": "#d4e8d4",
        "text_secondary": "#98b898",
        "accent": "#4ade80",
        "accent_hover": "#6ee7a0",
        "accent_glow": "rgba(74, 222, 128, 0.2)",
        "gradient_start": "#4ade80",
        "gradient_end": "#06b6d4",
        "border": "rgba(74, 222, 128, 0.1)",
    },
}


def get_themes():
    """Return available themes for the UI selector."""
    return {key: val["name"] for key, val in THEMES.items()}


def generate_portfolio(data, theme_id="dark"):
    """
    Generate a static portfolio site from GitHub data.
    
    Args:
        data: Dict from github_api.process_data()
        theme_id: Theme identifier (dark, ocean, sunset, forest)
    
    Returns:
        session_id: Unique ID for this generation session
    """
    theme = THEMES.get(theme_id, THEMES["dark"])
    session_id = str(uuid.uuid4())
    output_path = os.path.join(OUTPUT_DIR, session_id)

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=True,
    )
    env.filters["language_color"] = get_language_color

    # Render the portfolio HTML
    template = env.get_template("portfolio/template.html")
    rendered_html = template.render(
        profile=data["profile"],
        repos=data["repos"],
        languages=data["languages"],
        stats=data["stats"],
        theme=theme,
        theme_id=theme_id,
    )

    # Write the HTML file
    index_path = os.path.join(output_path, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    # Copy CSS and JS assets
    assets_output = os.path.join(output_path, "assets")
    if os.path.exists(PORTFOLIO_ASSETS_DIR):
        shutil.copytree(PORTFOLIO_ASSETS_DIR, assets_output, dirs_exist_ok=True)

    return session_id


def get_output_path(session_id):
    """Get the output directory path for a session."""
    return os.path.join(OUTPUT_DIR, session_id)


def create_zip(session_id):
    """
    Create a ZIP file of the generated portfolio.
    Returns the path to the ZIP file.
    """
    output_path = get_output_path(session_id)
    zip_path = os.path.join(OUTPUT_DIR, f"{session_id}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_path)
                zipf.write(file_path, arcname)

    return zip_path


def cleanup_session(session_id):
    """Remove generated files for a session."""
    output_path = get_output_path(session_id)
    zip_path = os.path.join(OUTPUT_DIR, f"{session_id}.zip")

    if os.path.exists(output_path):
        shutil.rmtree(output_path, ignore_errors=True)
    if os.path.exists(zip_path):
        os.remove(zip_path)
