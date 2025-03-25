def get_channel_data(channel_id):
    # ✅ Fetch YouTube API data dynamically
    youtube_data = fetch_youtube_data(channel_id)  # Your existing function

    # ✅ Extract required details
    channel_data = {
        "subscribers_growth": youtube_data['subscribers_growth'],
        "views_growth": youtube_data['views_growth']
    }
    
    video_data = youtube_data['videos']  # List of video details

    return channel_data, video_data
