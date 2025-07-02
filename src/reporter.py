import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import io
import base64
import os

def generate_html_report(test_case_dir: str):
    """
    Reads results.txt and generates a self-contained HTML report
    with a graph and a formatted table. The Positive column shows both the count and the percentage of total test cases.
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

    # Count the number of test case files in the directory (excluding .solution files)
    test_case_files = [f for f in os.listdir(test_case_dir) if os.path.isfile(os.path.join(test_case_dir, f)) and not f.endswith('.solution')]
    total_test_cases = len(test_case_files)
    if total_test_cases == 0:
        total_test_cases = 1  # Avoid division by zero

    # Add percentage to the Positive column
    def positive_with_percent(row):
        percent = 100 * row['positive'] / total_test_cases
        return f"{row['positive']}/{total_test_cases} ({percent:.0f}%)"
    data["Performance"] = data["positive"].apply(lambda x: int(x))  # Ensure integer
    data["Performance"] = data.apply(positive_with_percent, axis=1)

    # 1. Generate the 2D graph and encode it for HTML
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.scatter(data["positive"], data["false_positive"])

    for i, txt in enumerate(data["user_id"]):
        ax.annotate(
            txt,
            (data["positive"].iloc[i], data["false_positive"].iloc[i]),
            xytext=(5, 5), textcoords='offset points'
        )

    ax.set_xlabel("Positive (more is better)")
    ax.set_ylabel("False Positive (less is better)")
    ax.set_title("Benchmark Results: Positive vs. False Positive")
    ax.grid(True)

    # Save scatter plot to a memory buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    # 1b. Generate a bar graph for elapsed time
    fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=100)
    bars = ax2.bar(data["user_id"], data["elapsed_time"], color="#007bff")
    ax2.set_xlabel("User ID")
    ax2.set_ylabel("Elapsed Time (s)")
    ax2.set_title("Elapsed Time per Benchmark Run")
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    img_buffer2 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer2, format='png', bbox_inches='tight')
    img_buffer2.seek(0)
    img_base64_time = base64.b64encode(img_buffer2.getvalue()).decode('utf-8')
    plt.close(fig2)

    # 2. Prepare data for the HTML table
    data["date"] = pd.to_datetime(data["timestamp"], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
    data["elapsed_time"] = data["elapsed_time"].round(2)
    # Rename columns for display
    data.rename(columns={
        "date": "Date",
        "user_id": "User ID",
        # "positive": "Positive",  # Already replaced
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
            <h2>Elapsed Time per Benchmark Run</h2>
            <img src="data:image/png;base64,{img_base64_time}" alt="Elapsed Time Bar Graph">
            <h2>Results Table</h2>
            {html_table}
            <footer>
                <p>Report generated on {report_generation_time}</p>
                <p><a href=https://github.com/ortegaalfredo/simpleVulnBenchmark>https://github.com/ortegaalfredo/simpleVulnBenchmark</a></p>
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
    # Example usage: pass the test case directory as an argument
    import sys
    test_case_dir = sys.argv[1] if len(sys.argv) > 1 else "testcases/vulnerable"
    generate_html_report(test_case_dir) 
