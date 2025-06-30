import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import io
import base64

def generate_html_report():
    """
    Reads results.txt and generates a self-contained HTML report
    with a graph and a formatted table.
    """
    try:
        # Read the data from results.txt
        data = pd.read_csv(
            "results.txt",
            header=None,
            names=["timestamp", "user_id", "positive", "false_positive", "elapsed_time"]
        )
    except FileNotFoundError:
        print("Error: results.txt not found. Please run the benchmark first.")
        return
    except pd.errors.EmptyDataError:
        print("Error: results.txt is empty. No data to generate a report.")
        return

    # 1. Generate the 2D graph and encode it for HTML
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.scatter(data["positive"], data["false_positive"])

    for i, txt in enumerate(data["user_id"]):
        ax.annotate(
            txt,
            (data["positive"].iloc[i], data["false_positive"].iloc[i]),
            xytext=(5, 5), textcoords='offset points'
        )

    ax.set_xlabel("Positive")
    ax.set_ylabel("False Positive")
    ax.set_title("Benchmark Results: Positive vs. False Positive")
    ax.grid(True)

    # Save plot to a memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    # Encode buffer to base64
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    # 2. Prepare data for the HTML table
    data["date"] = pd.to_datetime(data["timestamp"], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
    data["elapsed_time"] = data["elapsed_time"].round(2)
    # Rename columns for display
    data.rename(columns={
        "date": "Date",
        "user_id": "User ID",
        "positive": "Positive",
        "false_positive": "False Positive",
        "elapsed_time": "Elapsed Time (s)"
    }, inplace=True)
    
    # Generate HTML table from DataFrame
    html_table = data.to_html(index=False, classes='results-table', border=0)

    # 3. Create the full HTML document
    report_generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Benchmark Results</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; background-color: #f8f9fa; color: #333; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1, h2 {{ text-align: center; color: #212529; }}
            img {{ display: block; margin: 20px auto; max-width: 100%; height: auto; border-radius: 8px; }}
            .results-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 0.9em;
            }}
            .results-table thead {{
                background-color: #007bff;
                color: #ffffff;
            }}
            .results-table th, .results-table td {{
                padding: 12px 15px;
                border: 1px solid #dee2e6;
                text-align: left;
            }}
            .results-table tbody tr:nth-of-type(even) {{
                background-color: #f8f9fa;
            }}
            .results-table tbody tr:hover {{
                background-color: #e9ecef;
            }}
            footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 0.8em;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Benchmark Report</h1>
            <h2>Results Graph</h2>
            <img src="data:image/png;base64,{img_base64}" alt="Benchmark Results Graph">
            <h2>Results Table</h2>
            {html_table}
            <footer>
                <p>Report generated on {report_generation_time}</p>
            </footer>
        </div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    with open("report.html", "w") as f:
        f.write(html_content)

    print("HTML report saved as report.html")

if __name__ == "__main__":
    generate_html_report() 