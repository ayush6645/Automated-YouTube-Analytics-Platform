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

    git clone https://github.com/ayush6645/Automated-YouTube-Analytics-Platform

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
