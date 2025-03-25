import { fetchVideoUploads, fetchSubscriberGrowth, fetchAnalytics } from "./api.js";

const ctxUploads = document.getElementById("uploadsChart").getContext("2d");
const ctxSubscribers = document.getElementById("subscribersChart").getContext("2d");
const ctxAnalytics = document.getElementById("analyticsChart").getContext("2d");

let uploadsChart, subscribersChart, analyticsChart;

// Function to render Video Uploads Chart
async function renderUploadsChart(channelId, timeframe = "month") {
    try {
        const data = await fetchVideoUploads(channelId, timeframe);
        if (!data || Object.keys(data).length === 0) {
            console.error("No data available for video uploads.");
            return;
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        if (uploadsChart) uploadsChart.destroy(); // Destroy previous chart

        uploadsChart = new Chart(ctxUploads, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Video Uploads",
                    data: values,
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    } catch (error) {
        console.error("Error rendering video uploads chart:", error);
    }
}

// Function to render Subscriber Growth Chart
async function renderSubscribersChart(channelId, timeframe = "month") {
    try {
        const data = await fetchSubscriberGrowth(channelId, timeframe);
        if (!data || Object.keys(data).length === 0) {
            console.error("No data available for subscriber growth.");
            return;
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        if (subscribersChart) subscribersChart.destroy();

        subscribersChart = new Chart(ctxSubscribers, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Subscriber Growth",
                    data: values,
                    backgroundColor: "rgba(255, 99, 132, 0.6)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 2
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    } catch (error) {
        console.error("Error rendering subscriber growth chart:", error);
    }
}

// Function to render Analytics Chart (Likes, Views, Engagement)
async function renderAnalyticsChart(channelId) {
    try {
        const data = await fetchAnalytics(channelId);
        if (!data || Object.keys(data).length === 0) {
            console.error("No analytics data available.");
            return;
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        if (analyticsChart) analyticsChart.destroy();

        analyticsChart = new Chart(ctxAnalytics, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{
                    label: "Engagement Metrics",
                    data: values,
                    backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    } catch (error) {
        console.error("Error rendering analytics chart:", error);
    }
}

// Function to update charts dynamically
async function updateCharts(channelId) {
    await renderUploadsChart(channelId);
    await renderSubscribersChart(channelId);
    await renderAnalyticsChart(channelId);
}

// Export functions for usage in other scripts
export { updateCharts, renderUploadsChart, renderSubscribersChart, renderAnalyticsChart };
