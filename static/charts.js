let chart;

async function fetchHistory(patientId = 1) {
    try {
        const response = await fetch(`/history/${patientId}`);
        const data = await response.json();

        const labels = data.map(d => d.timestamp);
        const heartRates = data.map(d => d.heart_rate);
        const spo2 = data.map(d => d.spo2);
        const temps = data.map(d => d.temperature);

        drawChart(labels, heartRates, spo2, temps);

    } catch (error) {
        console.log("Error fetching history");
    }
}

function drawChart(labels, hr, spo2, temp) {
    const ctx = document.getElementById("vitalsChart").getContext("2d");

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Heart Rate",
                    data: hr,
                    borderColor: "#ef4444",
                    tension: 0.3
                },
                {
                    label: "SpO₂",
                    data: spo2,
                    borderColor: "#22c55e",
                    tension: 0.3
                },
                {
                    label: "Temperature",
                    data: temp,
                    borderColor: "#38bdf8",
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true
        }
    });
}

// Load chart every 5 seconds
setInterval(fetchHistory, 5000);
fetchHistory();

/* Dark mode toggle */
const toggleBtn = document.getElementById("themeToggle");

if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light-mode");
    toggleBtn.innerText = "🌞 Light Mode";
}

toggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");

    if (document.body.classList.contains("light-mode")) {
        localStorage.setItem("theme", "light");
        toggleBtn.innerText = "🌞 Light Mode";
    } else {
        localStorage.setItem("theme", "dark");
        toggleBtn.innerText = "🌙 Dark Mode";
    }
});
