from flask import Flask, render_template, request
import json
import subprocess
import sys
import os

app = Flask(__name__)

# Safe top-level load for stock_data
try:
    with open("output.json", "r") as f:
        stock_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    stock_data = {}


@app.route("/", methods=["GET", "POST"])
def index():
    selected_key = None
    selected_value = None
    open_price = None
    last_refresh = None
    close_price = None
    plot_image = None
    bulletins = {}

    if request.method == "POST":
        selected_key = request.form.get("symbol_key")

        if selected_key in stock_data:
            selected_value = stock_data[selected_key]
            analysis_data = {}

            # Remove old file if present
            if os.path.exists("analysis_results.json"):
                os.remove("analysis_results.json")

            python_executable = sys.executable
            # Run background script
            subprocess.run([python_executable, "Stock_price.py", selected_key, selected_value])

            # Safely open results file
            if os.path.exists("analysis_results.json"):
                try:
                    with open("analysis_results.json", "r") as f:
                        analysis_data = json.load(f)
                except json.JSONDecodeError:
                    analysis_data = {}

            # Safe extraction using nested .get() chaining
            meta_data = analysis_data.get("meta_data", {})
            plot_data = analysis_data.get("Plot", {})

            last_refresh = meta_data.get("3. Last Refreshed")
            open_price = analysis_data.get("Open_price")
            close_price = analysis_data.get("last_close")
            bulletins = analysis_data.get("bulletins", {})
            plot_image = plot_data.get("plot_image")

    return render_template(
        "index.html",
        selected_key=selected_key,
        stock_data=stock_data,
        selected_value=selected_value,
        last_refresh=last_refresh,
        open_price=open_price,
        close_price=close_price,
        plot_image=plot_image,
        bulletins=bulletins
    )


if __name__ == "__main__":
    app.run(debug=True)