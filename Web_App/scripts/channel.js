document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const channelId = urlParams.get("channel_id");
    
    if (!channelId) {
        console.error("Channel ID is missing in the URL.");
        return;
    }
    
    fetchVideoUploads(channelId, "year");
    fetchVideoDurations(channelId, "year");
});

async function fetchData(endpoint, channelId, timeframe) {
    try {
        const response = await fetch(`/api/${endpoint}?channel_id=${channelId}&timeframe=${timeframe}`);
        const data = await response.json();

        if (!data || Object.keys(data).length === 0) {
            console.error(`No data available for ${endpoint}`);
            return null;
        }
        
        return data;
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

async function fetchVideoUploads(channelId, timeframe) {
    const data = await fetchData("video_uploads", channelId, timeframe);
    if (data && data.uploads) {
        renderChart("uploadsChart", "bar", "Video Uploads", data.uploads, "rgba(54, 162, 235, 0.6)", "rgba(54, 162, 235, 1)");
    }
}

async function fetchVideoDurations(channelId, timeframe) {
    const data = await fetchData("video_durations", channelId, timeframe);
    if (data && data.durations) {
        renderChart("durationsChart", "line", "Total Video Duration (Minutes)", data.durations, "rgba(255, 99, 132, 0.6)", "rgba(255, 99, 132, 1)");
    }
}

function renderChart(elementId, chartType, label, chartData, backgroundColor, borderColor) {
    const ctx = document.getElementById(elementId).getContext("2d");
    new Chart(ctx, {
        type: chartType,
        data: {
            labels: Object.keys(chartData),
            datasets: [{
                label: label,
                data: Object.values(chartData),
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}