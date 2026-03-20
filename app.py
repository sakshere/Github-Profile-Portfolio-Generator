"""
GitHub Portfolio Generator - Flask Application
Main entry point for the web application.
"""

import os
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from github_api import process_data
from generator import generate_portfolio, create_zip, get_output_path, get_themes, cleanup_session


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "github-portfolio-generator-secret-2024")

# Ensure output directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"), exist_ok=True)


@app.route("/")
def index():
    """Landing page with username input form."""
    themes = get_themes()
    return render_template("index.html", themes=themes)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Generate a portfolio from a GitHub username.
    Accepts JSON body with 'username' and optional 'theme'.
    Returns JSON with session_id for preview/download.
    """
    data = request.get_json()
    if not data or not data.get("username"):
        return jsonify({"error": "Please enter a GitHub username."}), 400

    username = data["username"].strip()
    theme_id = data.get("theme", "dark")

    # Validate username format
    if not username.isalnum() and not all(c.isalnum() or c == "-" for c in username):
        return jsonify({"error": "Invalid GitHub username format."}), 400

    try:
        # Fetch GitHub data
        github_data = process_data(username)

        # Generate the portfolio site
        session_id = generate_portfolio(github_data, theme_id)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "profile": github_data["profile"],
            "stats": github_data["stats"],
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


@app.route("/preview/<session_id>/")
def preview(session_id):
    """Serve the generated portfolio for preview."""
    output_path = get_output_path(session_id)
    index_path = os.path.join(output_path, "index.html")

    if not os.path.exists(index_path):
        return "Portfolio not found. Please generate again.", 404

    return send_file(index_path)


@app.route("/preview/<session_id>/assets/<path:filename>")
def preview_assets(session_id, filename):
    """Serve portfolio assets (CSS/JS) during preview."""
    assets_path = os.path.join(get_output_path(session_id), "assets")
    return send_from_directory(assets_path, filename)


@app.route("/download/<session_id>")
def download(session_id):
    """Download the generated portfolio as a ZIP file."""
    try:
        zip_path = create_zip(session_id)
        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"portfolio-{session_id[:8]}.zip"
        )
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == "__main__":
    print("\n🚀 GitHub Portfolio Generator")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
