document.getElementById("fetchDataBtn").addEventListener("click", fetchChannelData);

function fetchChannelData() {
    const inputChannelID = document.getElementById("channelIdInput").value.trim();
    const errorMessageBox = document.getElementById("errorMessage");

    if (!inputChannelID) {
        errorMessageBox.textContent = "Please enter a valid Channel ID.";
        errorMessageBox.classList.remove("hidden");
        return;
    }

    fetch("http://127.0.0.1:8000/fetch_channel_data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ channel_id: inputChannelID }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            window.location.href = `channel.html?channel_id=${data.channel_id}`;
        } else {
            errorMessageBox.textContent = "Invalid Channel ID.";
            errorMessageBox.classList.remove("hidden");
        }
    })
    .catch(error => {
        errorMessageBox.textContent = "Error fetching data.";
        errorMessageBox.classList.remove("hidden");
    });
}
