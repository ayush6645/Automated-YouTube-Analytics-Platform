import requests
import json
import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import plotly.express as px


# Initialize FastAPI app
app = FastAPI()

# ✅ Serve visualization images as static files
if not os.path.exists("visualizations"):
    os.makedirs("visualizations")

app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations")

# ✅ Function to generate visualizations dynamically
def generate_visualizations(channel_id, channel_data, video_data):
    output_dir = f"visualizations/{channel_id}"
    os.makedirs(output_dir, exist_ok=True)

    video_df = pd.DataFrame(video_data)
    
    # Subscriber Growth Over Time
    subscriber_growth_url = None
    if 'subscribers_growth' in channel_data:
        df_growth = pd.DataFrame(channel_data['subscribers_growth'])
        fig1 = px.line(df_growth, x='date', y='subscribers',
                       title='Subscriber Growth Over Time',
                       markers=True, template='plotly_dark')
        fig1.write_image(f"{output_dir}/subscriber_growth.png")
        subscriber_growth_url = f"/visualizations/{channel_id}/subscriber_growth.png"

    # Views Trend Over Time
    views_trend_url = None
    if 'views_growth' in channel_data:
        df_views = pd.DataFrame(channel_data['views_growth'])
        fig2 = px.area(df_views, x='date', y='views',
                       title='Views Trend Over Time', template='plotly_dark')
        fig2.write_image(f"{output_dir}/views_trend.png")
        views_trend_url = f"/visualizations/{channel_id}/views_trend.png"
    
    # Top 5 Videos by Views
    top_videos_url = None
    if 'views' in video_df.columns:
        top_videos = video_df.nlargest(5, 'views')
        fig3 = px.bar(top_videos, x='title', y='views',
                      title='Top 5 Videos by Views', color='views', text_auto=True, template='plotly_dark')
        fig3.write_image(f"{output_dir}/top_videos.png")
        top_videos_url = f"/visualizations/{channel_id}/top_videos.png"
    
    return {
        "subscriber_growth": subscriber_growth_url,
        "views_trend": views_trend_url,
        "top_videos": top_videos_url
    }

# ✅ API to Fetch Data in Real-Time and Generate Graphs
@app.get("/video_analytics/{channel_id}")
def video_analytics(channel_id: str):
    # ✅ Step 1: Fetch real-time data
    channel_data, video_data = fetch_channel_data(channel_id)

    if not channel_data or not video_data:
        return {"error": "Failed to fetch channel data"}

    # ✅ Step 2: Generate visualizations dynamically
    visualization_urls = generate_visualizations(channel_id, channel_data, video_data)

    return {
        "message": "Visualizations generated successfully",
        "graphs": visualization_urls
    }




from googleapiclient.discovery import build
import datetime

# ✅ Function to fetch real-time data
def fetch_channel_data(channel_id):
    api_key = "AIzaSyC6Ok9yHHF1uAIzxewABAc5wNNm9Iz-J-8"  # Replace with your actual API key
    youtube = build('youtube', 'v3', developerKey=api_key)

    # ✅ Fetch Channel Stats
    request = youtube.channels().list(
        part="statistics,snippet",
        id=channel_id
    )
    response = request.execute()

    if not response["items"]:
        return None, None  # No channel found

    channel_info = response["items"][0]
    subscribers = int(channel_info["statistics"]["subscriberCount"])
    views = int(channel_info["statistics"]["viewCount"])
    
    # ✅ Generate Fake Growth Data (For visualization purposes)
    today = datetime.date.today()
    channel_data = {
        "subscribers_growth": [
            {"date": str(today - datetime.timedelta(days=30)), "subscribers": subscribers - 500},
            {"date": str(today), "subscribers": subscribers}
        ],
        "views_growth": [
            {"date": str(today - datetime.timedelta(days=30)), "views": views - 10000},
            {"date": str(today), "views": views}
        ]
    }

    # ✅ Fetch Video Data
    video_request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50,
        order="date",
        type="video"
    )
    video_response = video_request.execute()

    video_data = []
    for item in video_response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        
        # Fetch video stats
        video_stats_request = youtube.videos().list(
            part="statistics",
            id=video_id
        )
        video_stats_response = video_stats_request.execute()

        if video_stats_response["items"]:
            views = int(video_stats_response["items"][0]["statistics"].get("viewCount", 0))
            video_data.append({"title": title, "views": views})

    return channel_data, video_data



# Constants
API_KEY = "AIzaSyC6Ok9yHHF1uAIzxewABAc5wNNm9Iz-J-8"
BASE_URL = "https://www.googleapis.com/youtube/v3"

def get_channel_data(channel_id):
    url = f"{BASE_URL}/channels?part=statistics&id={channel_id}&key={API_KEY}"
    response = requests.get(url).json()
    stats = response['items'][0]['statistics']
    return {
        "total_videos": int(stats.get("videoCount", 0)),
        "total_subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "engagement_rate": (int(stats.get("likeCount", 0)) + int(stats.get("commentCount", 0))) / max(int(stats.get("viewCount", 1)), 1)
    }

@app.get("/channel/{channel_id}")
def channel_analytics(channel_id: str):
    data = get_channel_data(channel_id)
    return {"channel_analytics": data}

def get_video_details(channel_id):
    video_data = []
    url = f"{BASE_URL}/search?key={API_KEY}&channelId={channel_id}&part=id&order=date&maxResults=50"
    response = requests.get(url).json()
    for item in response.get("items", []):
        video_id = item["id"].get("videoId")
        if video_id:
            vid_url = f"{BASE_URL}/videos?part=statistics,snippet,contentDetails&id={video_id}&key={API_KEY}"
            vid_response = requests.get(vid_url).json()
            stats = vid_response["items"][0]["statistics"]
            snippet = vid_response["items"][0]["snippet"]
            duration = vid_response["items"][0]["contentDetails"]["duration"]
            
            likes = int(stats.get("likeCount", 0))
            views = int(stats.get("viewCount", 0))
            comments = int(stats.get("commentCount", 0))
            engagement_rate = (likes + comments) / max(views, 1)
            like_ratio = likes / max(views, 1)
            comment_ratio = comments / max(views, 1)
            
            video_data.append({
                "video_id": video_id,
                "title": snippet["title"],
                "views": views,
                "likes": likes,
                "comments": comments,
                "published_at": snippet["publishedAt"][:10],
                "engagement_rate": engagement_rate,
                "like_ratio": like_ratio,
                "comment_ratio": comment_ratio,
                "duration": duration
            })
    
    sorted_videos = sorted(video_data, key=lambda x: x["views"], reverse=True)
    
    df = pd.DataFrame(video_data)
    df['published_at'] = pd.to_datetime(df['published_at'])
    recent_period = datetime.now() - timedelta(weeks=4)
    trending_videos = df[df['published_at'] > recent_period].sort_values(by='views', ascending=False).head(5).to_dict('records')
    
    upload_frequency = "Daily" if df['published_at'].diff().dt.days.mean() <= 1 else "Weekly" if df['published_at'].diff().dt.days.mean() <= 7 else "Monthly"
    popular_upload_day = df['published_at'].dt.day_name().mode()[0] if not df.empty else "Unknown"
    
    return {
        "video_analytics": sorted_videos,
        "top_performing_video": sorted_videos[0] if sorted_videos else None,
        "top_5_most_viewed": sorted_videos[:5],
        "top_5_most_liked": sorted(video_data, key=lambda x: x["likes"], reverse=True)[:5],
        "top_5_most_engaging": sorted(video_data, key=lambda x: x["engagement_rate"], reverse=True)[:5],
        "longest_video": max(video_data, key=lambda x: x["duration"], default=None),
        "shortest_video": min(video_data, key=lambda x: x["duration"], default=None),
        "trending_videos": trending_videos,
        "upload_frequency": upload_frequency,
        "most_popular_upload_day": popular_upload_day
    }

@app.get("/videos/{channel_id}")
def video_analytics(channel_id: str):
    data = get_video_details(channel_id)
    return data

def calculate_revenue_estimate(view_count, cpm=1.5):
    return (view_count / 1000) * cpm

@app.get("/revenue/{channel_id}")
def revenue_estimation(channel_id: str):
    data = get_channel_data(channel_id)
    revenue = calculate_revenue_estimate(data["total_views"])
    return {"estimated_revenue": revenue, "cpm": 1.5}

@app.get("/best_time/{channel_id}")
def best_posting_time(channel_id: str):
    video_data = get_video_details(channel_id)["video_analytics"]
    df = pd.DataFrame(video_data)
    df['published_at'] = pd.to_datetime(df['published_at'])
    best_day = df['published_at'].dt.day_name().mode()[0] if not df.empty else "Unknown"
    return {"best_posting_day": best_day, "insight": "Posting on this day might increase engagement"}

@app.get("/compare/{channel_1}/{channel_2}")
def channel_comparison(channel_1: str, channel_2: str):
    data_1 = get_channel_data(channel_1)
    data_2 = get_channel_data(channel_2)
    return {
        "channel_1": {
            "subscribers": data_1["total_subscribers"],
            "views": data_1["total_views"],
            "videos": data_1["total_videos"]
        },
        "channel_2": {
            "subscribers": data_2["total_subscribers"],
            "views": data_2["total_views"],
            "videos": data_2["total_videos"]
        },
        "comparison": {
            "subscribers_difference": abs(data_1["total_subscribers"] - data_2["total_subscribers"]),
            "views_difference": abs(data_1["total_views"] - data_2["total_views"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
