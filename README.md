  YouTube Data Analytics Platform - README /\* General Styles \*/ body { font-family: 'Arial', sans-serif; line-height: 1.8; background: linear-gradient(to right, #e0eafc, #cfdef3); color: #333; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; } /\* Container \*/ .container { max-width: 900px; background: #ffffff; padding: 30px; border-radius: 16px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease; } .container:hover { transform: translateY(-5px); } /\* Headings \*/ h1, h2, h3 { color: #2c3e50; font-weight: 700; margin-bottom: 10px; border-bottom: 2px solid #3498db; padding-bottom: 5px; transition: color 0.3s; } h1:hover, h2:hover, h3:hover { color: #2980b9; } /\* Lists \*/ ul { padding-left: 20px; list-style-type: none; } ul li { padding-left: 20px; position: relative; margin-bottom: 8px; transition: transform 0.2s ease; } ul li::before { content: '✔'; position: absolute; left: 0; color: #27ae60; font-weight: bold; } ul li:hover { transform: translateX(5px); } /\* Code Block \*/ code { background-color: #f4f4f4; padding: 4px 6px; border-radius: 4px; font-family: 'Courier New', Courier, monospace; color: #c0392b; } pre { background-color: #f4f4f4; padding: 12px; overflow-x: auto; border-left: 4px solid #3498db; border-radius: 6px; font-size: 14px; color: #333; white-space: pre-wrap; transition: background-color 0.3s; } pre:hover { background-color: #ecf0f1; } /\* Buttons and Links \*/ a { color: #3498db; text-decoration: none; transition: color 0.3s; } a:hover { color: #2980b9; } /\* Ordered List \*/ ol { padding-left: 20px; } ol li { margin-bottom: 8px; font-weight: 500; color: #34495e; } /\* Footer \*/ .footer { margin-top: 30px; text-align: center; font-size: 14px; color: #7f8c8d; }

📌 YouTube Data Analytics Platform
==================================

This project is a YouTube Data Analytics Platform built using Python, Kafka, Hadoop, and Power BI. It automates real-time data extraction from YouTube, processes it using Kafka, and stores it in Hadoop HDFS every 15 minutes. The platform offers advanced analytics and dynamic visualizations through a web-based interface.

🚀 Features
-----------

### ✅ Data Extraction

*   Total video uploads
*   Total video duration
*   Total likes, views, and subscribers

### ✅ Data Processing

*   Real-time data extraction every 15 minutes using Kafka
*   Data stored in Hadoop HDFS
*   End date selection for automated data collection

### ✅ Data Visualization

*   Dynamic charts and graphs using Power BI and Python
*   Subscriber and likes growth (yearly/monthly)
*   Top video performance analysis

### ✅ Advanced Analytics

*   Sentiment analysis on comments (positive, negative, neutral)
*   Category-based analysis (content performance)
*   Time-series analysis (views, likes, subscribers over time)
*   Hashtag & keyword analysis (trending topics)
*   Audience retention metrics (watch time, drop-off points)
*   Channel comparison and revenue estimation

🛠️ Tech Stack
--------------

*   **Backend:** Python, Kafka, Hadoop HDFS
*   **Frontend:** HTML, CSS, JavaScript
*   **Visualization:** Power BI, Python
*   **Data Storage:** Hadoop HDFS
*   **Message Broker:** Kafka

📁 Project Structure
--------------------

📂 YouTube\_Data\_Engineering
├── 📂 scripts
│   └── backend.py
├── 📂 Web\_App
│   ├── index.html
│   └── channel.html
└── README.md
    

🔥 How to Run
-------------

1.  Clone the repository:

    git clone https://github.com/your-username/YouTube-Data-Analytics.git

3.  Install dependencies:

    pip install -r requirements.txt

5.  Start Kafka and Hadoop services.
6.  Run the backend:

    python scripts/backend.py

8.  Open the web app:

*   Open `channel.html` in your browser.
*   Enter a YouTube Channel ID and start the analysis.

🤝 Contributing
---------------

Feel free to contribute by raising issues or submitting pull requests!

📄 License
----------

This project is licensed under the MIT License.

Built by Gyan Gupta
