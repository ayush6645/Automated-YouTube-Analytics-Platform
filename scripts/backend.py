from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime
import os
import uvicorn
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from collections import defaultdict
from flask import Flask, request, jsonify
from flask import Flask
from flask_cors import CORS
import isodate
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from textblob import TextBlob
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator
from deep_translator import GoogleTranslator
from nltk.sentiment import SentimentIntensityAnalyzer
import html
import httpx
from googleapiclient.discovery import build
from kafka import KafkaProducer
from hdfs import InsecureClient
import json
import time
from threading import Thread
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()
  # Enable CORS for all routes

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class ChannelRequest(BaseModel):
    channel_id: str

YOUTUBE_API_KEY = "AIzaSyC6Ok9yHHF1uAIzxewABAc5wNNm9Iz-J-8"

@app.post("/fetch_channel_data")
async def fetch_channel_data(request: ChannelRequest):
    channel_info = fetch_channel_details(request.channel_id)
    return channel_info if channel_info else {"message": "Invalid Channel ID", "valid": False}

def is_valid_channel(channel_id):
    """Check if the YouTube channel ID is valid."""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&id={channel_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return "items" in data and len(data["items"]) > 0

def get_channel_info(channel_id):
    """Fetch YouTube channel details, including the name."""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "items" in data and len(data["items"]) > 0:
        return data["items"][0]["snippet"]["title"]
    return None


def get_subscriber_growth(channel_id: str):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "items" not in data:
        return {"error": "Invalid Channel ID or API Limit Reached"}

    subscribers = int(data["items"][0]["statistics"]["subscriberCount"])

    # Simulate time-series data (replace with real stored historical data)
    dates = [
        "Jan 2023", "Jun 2023", "Dec 2023", "Mar 2024", datetime.now().strftime("%b %Y")
    ]
    subscriber_counts = [
        subscribers - 50000, subscribers - 30000, subscribers - 10000, subscribers - 5000, subscribers
    ]

    return {"dates": dates, "subscribers": subscriber_counts}

@app.get("/get_subscriber_growth")
async def subscriber_growth(channel_id: str):
    return get_subscriber_growth(channel_id)

def fetch_channel_details(channel_id):
    """Fetch detailed channel information from YouTube API."""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        return None

    channel = data["items"][0]

    return {
        "channel_id": channel_id,
        "channel_name": channel["snippet"]["title"],
        "profile_image": channel["snippet"]["thumbnails"]["high"]["url"],
        "subscribers": channel["statistics"].get("subscriberCount", "N/A"),
        "total_videos": channel["statistics"].get("videoCount", "N/A"),
        "total_views": channel["statistics"].get("viewCount", "N/A"),
        "about": channel["snippet"].get("description", "No description available"),
        "valid": True
    }


@app.get("/get_uploads_per_month")
async def get_video_uploads(channel_id: str):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=50&order=date&type=video&key={YOUTUBE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    if "items" not in data:
        return {"error": "No videos found or API limit reached."}

    video_counts = defaultdict(int)

    for video in data["items"]:
        published_at = video["snippet"]["publishedAt"]
        date_obj = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")

        # Aggregate by month and year (YYYY-MM format)
        key = date_obj.strftime("%Y-%m")
        video_counts[key] += 1

    # Convert to list of dicts for better compatibility with frontend
    result = [{"month": key, "uploads": value} for key, value in sorted(video_counts.items())]

    return result


def fetch_all_video_upload_dates(channel_id):
    """Fetch all video upload dates for a given channel."""
    upload_dates = []
    next_page_token = None
    base_url = "https://www.googleapis.com/youtube/v3/search"

    while True:
        params = {
            "key": YOUTUBE_API_KEY,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": 50,
            "type": "video",
            "pageToken": next_page_token,
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if "error" in data:
            return {"error": data["error"]["message"]}

        for item in data.get("items", []):
            video_date = item["snippet"]["publishedAt"].split("T")[0]
            upload_dates.append(video_date)

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return upload_dates


@app.get("/get_lifetime_uploads")
async def get_lifetime_uploads(channel_id: str):
    """API endpoint to return all video upload dates."""
    upload_dates = fetch_all_video_upload_dates(channel_id)

    if isinstance(upload_dates, dict) and "error" in upload_dates:
        return upload_dates
    
    # Convert to list of dicts for frontend compatibility
    result = [{"date": date} for date in upload_dates]

    return result

@app.get("/api/video_durations")
async def get_video_durations(channel_id: str):
    try:
        # Step 1: Fetch all videos for the given channel
        videos = fetch_video_data(channel_id)
        if not videos:
            return {"error": "No videos found for this channel."}

        # Step 2: Process video durations and group by month
        durations_by_month = {}

        for video in videos:
            published_date = video["publishedAt"]
            duration_minutes = video["duration"]

            # Extract year-month from published date
            month_key = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m")

            # Sum the durations per month
            durations_by_month[month_key] = durations_by_month.get(month_key, 0) + duration_minutes

        return {"durations": durations_by_month}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch all videos for a channel without using playlists
def fetch_video_data(channel_id):
    video_ids = []
    next_page_token = None

    # Step 1: Get video IDs using the search API
    while True:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=id&channelId={channel_id}&maxResults=50&type=video&key={YOUTUBE_API_KEY}"
        if next_page_token:
            search_url += f"&pageToken={next_page_token}"
        
        search_response = requests.get(search_url).json()
        
        if "items" in search_response:
            for item in search_response["items"]:
                if "videoId" in item["id"]:
                    video_ids.append(item["id"]["videoId"])
        
        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break  # Stop if no more pages

    # Step 2: Fetch video details (duration) using video IDs
    videos_data = []
    for i in range(0, len(video_ids), 50):  # API allows max 50 videos per request
        video_ids_batch = ",".join(video_ids[i:i+50])
        video_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={video_ids_batch}&key={YOUTUBE_API_KEY}"
        video_response = requests.get(video_url).json()

        if "items" in video_response:
            for item in video_response["items"]:
                published_at = item["snippet"]["publishedAt"]
                duration_iso = item["contentDetails"]["duration"]
                duration_minutes = convert_duration_to_minutes(duration_iso)
                
                videos_data.append({"publishedAt": published_at, "duration": duration_minutes})

    return videos_data

# Convert ISO duration to minutes
def convert_duration_to_minutes(duration_iso):
    duration = isodate.parse_duration(duration_iso)
    return int(duration.total_seconds() // 60)  # Convert seconds to minutes


def get_channel_videos(channel_id):
    """
    Fetches all video IDs from a given YouTube channel.
    """
    video_list = []
    next_page_token = None

    while True:
        url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={channel_id}&part=id&type=video&maxResults=50"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        
        response = requests.get(url).json()
        if "items" not in response:
            break

        for item in response["items"]:
            video_list.append(item["id"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_list

def get_video_details(video_ids):
    """
    Fetches video details (views, likes, comments) for given video IDs.
    """
    video_details = []
    ids_string = ",".join(video_ids)

    url = f"https://www.googleapis.com/youtube/v3/videos?key={YOUTUBE_API_KEY}&id={ids_string}&part=snippet,statistics"
    response = requests.get(url).json()

    for item in response.get("items", []):
        video_details.append({
            "title": item["snippet"]["title"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        })

    return video_details
@app.get("/get_top_videos")
def get_top_videos(channel_id: str):
    try:
        # Fetch videos sorted by views
        url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={channel_id}&part=snippet&type=video&order=viewCount&maxResults=3"
        response = requests.get(url)
        data = response.json()

        if "items" not in data:
            return JSONResponse(content={"error": "Invalid response from YouTube API"}, status_code=400)

        top_videos = []
        for item in data["items"]:
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]

            # Fetch video statistics
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?key={YOUTUBE_API_KEY}&id={video_id}&part=statistics"
            stats_response = requests.get(stats_url).json()

            if "items" in stats_response and stats_response["items"]:
                stats = stats_response["items"][0]["statistics"]
                views = int(stats.get("viewCount", 0))
                likes = int(stats.get("likeCount", 0))
                comments = int(stats.get("commentCount", 0))

                top_videos.append({
                    "title": video_title,
                    "views": views,
                    "likes": likes,
                    "comments": comments
                })

        return JSONResponse(content=top_videos, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.route('/get_top_videos', methods=['GET'])
def fetch_top_videos():
    channel_id = request.args.get("channel_id")
    if not channel_id:
        return jsonify({"error": "Channel ID is required"}), 400

    video_data = get_top_videos(channel_id)
    return jsonify(video_data)
# Fetch comments asynchronously
async def get_comments(video_id):
    comments = []
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={YOUTUBE_API_KEY}&maxResults=100"

    async with httpx.AsyncClient() as client:
        while url:
            try:
                response = await client.get(url)
                data = response.json()

                if 'error' in data:
                    error_message = data['error'].get('message', 'API error occurred')
                    raise HTTPException(status_code=400, detail=error_message)

                if "items" not in data:
                    return {"error": "No comments found or API limit reached."}
                
                for item in data["items"]:
                    comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    comments.append(comment)

                # Handle pagination
                next_page_token = data.get("nextPageToken")
                if next_page_token:
                    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={YOUTUBE_API_KEY}&maxResults=100&pageToken={next_page_token}"
                else:
                    break
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    return comments

# Translate comment to English using deep_translator
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        return text  # If translation fails, return the original comment

# Analyze sentiment using nltk
def analyze_sentiment(comments):
    if not comments:
        return {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "conclusion": "No comments to analyze."
        }

    analyzer = SentimentIntensityAnalyzer()
    positive, negative, neutral = 0, 0, 0

    for comment in comments:
        # Clean comment text (remove non-ASCII and HTML entities)
        cleaned_comment = html.unescape(re.sub(r'[^\x00-\x7F]+', '', comment))

        # Translate to English
        translated_comment = translate_to_english(cleaned_comment)

        # Analyze sentiment
        sentiment = analyzer.polarity_scores(translated_comment)
        if sentiment['compound'] > 0.05:
            positive += 1
        elif sentiment['compound'] < -0.05:
            negative += 1
        else:
            neutral += 1
    
    total = positive + negative + neutral
    
    positive_percentage = round((positive / total) * 100, 2)
    negative_percentage = round((negative / total) * 100, 2)
    neutral_percentage = round((neutral / total) * 100, 2)

    if positive_percentage > negative_percentage:
        conclusion = "Overall positive sentiment."
    elif negative_percentage > positive_percentage:
        conclusion = "Overall negative sentiment."
    else:
        conclusion = "Mixed or neutral sentiment."

    return {
        "positive": positive_percentage,
        "negative": negative_percentage,
        "neutral": neutral_percentage,
        "conclusion": conclusion
    }

# API endpoint for sentiment analysis
@app.post("/analyze")
async def analyze_sentiment_endpoint(data: dict):
    video_id = data.get('videoId')

    if not video_id:
        raise HTTPException(status_code=400, detail="Video ID is required")

    # Fetch comments
    comments = await get_comments(video_id)

    if 'error' in comments:
        return JSONResponse(status_code=400, content={"error": comments['error']})

    # Analyze sentiment
    sentiment_result = analyze_sentiment(comments)
    
    return sentiment_result

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from kafka import KafkaProducer
from hdfs import InsecureClient
from datetime import datetime
import json
import logging
import time
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# ------------------ GET TOTAL LIKES ------------------ #
def get_total_likes(channel_id):
    try:
        total_likes = 0
        video_ids = []
        next_page_token = None

        # Step 1: Get all video IDs from the channel
        while True:
            search_response = requests.get(
                f"https://www.googleapis.com/youtube/v3/search?channelId={channel_id}&part=id&maxResults=50&pageToken={next_page_token}&key={YOUTUBE_API_KEY}"
            ).json()

            for item in search_response.get("items", []):
                if item["id"].get("videoId"):
                    video_ids.append(item["id"]["videoId"])

            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                break

        # Step 2: Get likes for each video using video IDs
        for i in range(0, len(video_ids), 50):
            video_response = requests.get(
                f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={','.join(video_ids[i:i + 50])}&key={YOUTUBE_API_KEY}"
            ).json()

            for video in video_response.get("items", []):
                likes = int(video["statistics"].get("likeCount", 0))
                total_likes += likes

        logging.info(f"Total likes: {total_likes}")
        return total_likes

    except Exception as e:
        logging.error(f"Error fetching likes: {e}")
        return 0


# ------------------ KAFKA CONFIGURATION ------------------ #
KAFKA_TOPIC = 'youtube_data'
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
# ------------------ HDFS CONFIGURATION ------------------ #
HDFS_URL = 'http://localhost:9870'  # Updated port to 9870
HDFS_DIR = '/youtube_data/'
client = InsecureClient(HDFS_URL, user='hadoop')


# ------------------ LOGGING ------------------ #
logging.basicConfig(level=logging.INFO)

# ------------------ MODELS ------------------ #
class AutomationRequest(BaseModel):
    channel_id: str
    start_date: str
    end_date: str

# ------------------ TASK: SEND DATA TO KAFKA & HDFS ------------------ #
def task(channel_id):
    try:
        channel_info = fetch_channel_details(channel_id)
        if not channel_info:
            logging.error("Invalid channel ID")
            return

        total_likes = get_total_likes(channel_id)

        data = {
            "channel_id": channel_id,
            "channel_name": channel_info["channel_name"],
            "total_views": channel_info["total_views"],
            "total_likes": total_likes,
            "total_subscribers": channel_info["subscribers"],
            "total_videos": channel_info["total_videos"],
            "timestamp": datetime.now().isoformat()
        }

        # ✅ Send data to Kafka
        producer.send(KAFKA_TOPIC, value=data)
        logging.info(f"✅ Sent data to Kafka: {data}")

        # ✅ Save data to HDFS
        file_path = f"{HDFS_DIR}{channel_id}_{int(time.time())}.json"
        with client.write(file_path, encoding='utf-8') as writer:
            writer.write(json.dumps(data))
        logging.info(f"✅ Saved data to HDFS: {file_path}")

    except Exception as e:
        logging.error(f"❌ Error during task execution: {e}")

# ------------------ AUTOMATION FUNCTION ------------------ #
def start_streaming(channel_id, end_date):
    end_time = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    while datetime.now() < end_time:
        task(channel_id)
        logging.info("✅ Data collected successfully. Sleeping for 15 minutes...")
        time.sleep(15 * 60)  # Sleep for 15 minutes

# ------------------ START AUTOMATION ENDPOINT ------------------ #
@app.post("/start-automation")
async def start_automation(request: AutomationRequest, background_tasks: BackgroundTasks):
    channel_id = request.channel_id
    start_date = request.start_date
    end_date = request.end_date

    # ✅ Validate date format and future end date
    try:
        start_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

        if end_time <= datetime.now():
            raise HTTPException(status_code=400, detail="End date must be in the future")
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS")

    # ✅ Start automation in the background
    background_tasks.add_task(start_streaming, channel_id, end_date)

    logging.info(f"✅ Automation started for channel ID: {channel_id} until {end_date}")
    return {"message": "Automation started successfully!", "channel_id": channel_id, "end_date": end_date}

# ------------------ SERVE FRONTEND ------------------ #
frontend_path = Path(__file__).parent.parent / "Web_App"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(frontend_path / "index.html")

@app.get("/channel.html")
async def serve_channel():
    return FileResponse(frontend_path / "channel.html")

# ✅ Start FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
