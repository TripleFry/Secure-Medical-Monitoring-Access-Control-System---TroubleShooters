let hrChart, spo2Chart, tempChart;

async function fetchHistory(patientId = 1) {
    try {
        const response = await fetch(`/history/${patientId}`);
        const data = await response.json();

        console.log("Fetched data:", data);

        if (!data || data.length === 0) {
            console.log("No data available");
            return;
        }

        const labels = data.map(d => {
            const date = new Date(d.timestamp);
            return date.toLocaleTimeString();
        });
        const heartRates = data.map(d => d.heart_rate);
        const spo2 = data.map(d => d.spo2);
        const temps = data.map(d => d.temperature);

        drawCharts(labels, heartRates, spo2, temps);

    } catch (error) {
        console.error("Error fetching history:", error);
    }
}

function drawCharts(labels, hr, spo2Data, temp) {
    // Heart Rate Chart
    const hrCtx = document.getElementById("hrChart");
    if (hrCtx) {
        if (hrChart) {
            hrChart.destroy();
        }

        hrChart = new Chart(hrCtx.getContext("2d"), {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Heart Rate (bpm)",
                    data: hr,
                    borderColor: "#e53935",
                    backgroundColor: "rgba(229, 57, 53, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 40,
                        max: 120,
                        title: {
                            display: true,
                            text: 'BPM'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        });
    }

    // SpO2 Chart
    const spo2Ctx = document.getElementById("spo2Chart");
    if (spo2Ctx) {
        if (spo2Chart) {
            spo2Chart.destroy();
        }

        spo2Chart = new Chart(spo2Ctx.getContext("2d"), {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Blood Oxygen (%)",
                    data: spo2Data,
                    borderColor: "#00c853",
                    backgroundColor: "rgba(0, 200, 83, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 85,
                        max: 100,
                        title: {
                            display: true,
                            text: 'SpO₂ %'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        });
    }

    // Temperature Chart
    const tempCtx = document.getElementById("tempChart");
    if (tempCtx) {
        if (tempChart) {
            tempChart.destroy();
        }

        tempChart = new Chart(tempCtx.getContext("2d"), {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Temperature (°C)",
                    data: temp,
                    borderColor: "#0066cc",
                    backgroundColor: "rgba(0, 102, 204, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 35,
                        max: 40,
                        title: {
                            display: true,
                            text: 'Temperature °C'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                }
            }
        });
    }
}

// Expose renderCharts function for the template
window.renderCharts = function (patientId) {
    fetchHistory(patientId);
};

// Auto-refresh every 5 seconds
setInterval(() => {
    const patientId = document.getElementById('patientId')?.value || 1;
    fetchHistory(patientId);
}, 5000);

// Load charts on page load
window.addEventListener('load', () => {
    const patientId = document.getElementById('patientId')?.value || 1;
    fetchHistory(patientId);
});
