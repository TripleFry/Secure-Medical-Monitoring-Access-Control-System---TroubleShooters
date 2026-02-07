/**
 * charts.js - Handles rendering of Chart.js charts for the Analytics page.
 */

// Global chart instances for destruction/re-creation
let charts = {};

async function fetchHistory(url) {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${url}:`, error);
        return [];
    }
}

function createChart(id, label, labels, data, color, unit) {
    const ctx = document.getElementById(id).getContext('2d');

    // Destroy existing chart if it exists
    if (charts[id]) {
        charts[id].destroy();
    }

    charts[id] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${label} (${unit})`,
                data: data,
                borderColor: color,
                backgroundColor: color + '22',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--gray-800').trim() || '#1e293b'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--gray-200').trim() || '#e2e8f0'
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--gray-600').trim() || '#475569'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--gray-600').trim() || '#475569',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

async function renderCharts(patientId) {
    // 1. Render Vitals Charts
    const vitalsData = await fetchHistory(`/api/history/vitals/${patientId}`);
    if (vitalsData && vitalsData.length > 0) {
        const timestamps = vitalsData.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

        createChart('hrChart', 'Heart Rate', timestamps, vitalsData.map(d => d.heart_rate), '#ef4444', 'bpm');
        createChart('spo2Chart', 'SpO2', timestamps, vitalsData.map(d => d.spo2), '#3b82f6', '%');
        createChart('tempChart', 'Body Temp', timestamps, vitalsData.map(d => d.temperature), '#10b981', '°C');
    }



    // 2. Render Environmental Charts
    const envData = await fetchHistory('/api/history/env');
    if (envData && envData.length > 0) {
        const timestamps = envData.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

        createChart('humidityChart', 'Humidity', timestamps, envData.map(d => d.humidity), '#06b6d4', '%');
        createChart('roomTempChart', 'Room Temp', timestamps, envData.map(d => d.room_temp), '#f59e0b', '°C');
        createChart('aqiChart', 'Air Quality (AQI)', timestamps, envData.map(d => d.aqi), '#8b5cf6', 'index');
    }
}

// Export to window scope
window.renderCharts = renderCharts;
