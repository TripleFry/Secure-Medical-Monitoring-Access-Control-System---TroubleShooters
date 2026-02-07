let lastAlert = "";

// Fetch and update dashboard data
async function fetchData() {
    try {
        const response = await fetch("/data");
        const data = await response.json();

        // Update access status with color coding
        const accessEl = document.getElementById("access");
        if (accessEl) {
            accessEl.innerText = data.access_status || "Monitoring...";
            
            // Color code access status
            if (data.access_status?.toLowerCase().includes("authorized")) {
                accessEl.style.color = "#10b981";
                accessEl.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
                accessEl.style.webkitBackgroundClip = "text";
                accessEl.style.webkitTextFillColor = "transparent";
            } else if (data.access_status?.toLowerCase().includes("intruder")) {
                accessEl.style.color = "#ef4444";
                accessEl.style.background = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)";
                accessEl.style.webkitBackgroundClip = "text";
                accessEl.style.webkitTextFillColor = "transparent";
            }
        }

        // Update alert status
        const alertEl = document.getElementById("alert");
        if (alertEl) {
            alertEl.innerText = data.alert || "All Clear";
            
            // Animate if new alert
            if (data.alert && data.alert !== lastAlert) {
                alertEl.classList.add('pulse-alert');
                setTimeout(() => alertEl.classList.remove('pulse-alert'), 3000);
                lastAlert = data.alert;
            }
        }

        // Update vitals with smooth transitions
        updateValue("hr", data.heart_rate);
        updateValue("spo2", data.spo2);
        updateValue("temp", data.temperature);

        // Update risk level with color coding
        const riskEl = document.getElementById("risk");
        if (riskEl) {
            const riskValue = data.risk || "Normal";
            riskEl.innerText = riskValue;
            
            // Color code risk level
            if (riskValue === "High") {
                riskEl.style.background = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)";
            } else if (riskValue === "Medium") {
                riskEl.style.background = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)";
            } else {
                riskEl.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
            }
            riskEl.style.webkitBackgroundClip = "text";
            riskEl.style.webkitTextFillColor = "transparent";
        }

        // Update profile information
        updateValue("name", data.name || "John Doe");
        updateValue("age", data.age || "--");
        updateValue("gender", data.gender || "--");
        updateValue("smoking", data.smoking ? "Yes" : "No");
        updateValue("hypertension", data.hypertension ? "Yes" : "No");

    } catch (error) {
        console.log("Error fetching data:", error);
    }
}

// Smooth value update helper
function updateValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element && value !== undefined && value !== null) {
        element.innerText = value;
    }
}

// Auto-refresh every 2 seconds
setInterval(fetchData, 2000);
fetchData();

// Theme toggle functionality
const toggleBtn = document.getElementById("themeToggle");

if (toggleBtn) {
    // Load saved theme preference
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        document.body.classList.add("light-mode");
        toggleBtn.innerText = "☀️ Light Mode";
    } else {
        toggleBtn.innerText = "🌙 Dark Mode";
    }

    // Toggle theme on button click
    toggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("light-mode");
        
        // Add smooth transition animation
        document.body.style.transition = "all 0.5s ease";

        if (document.body.classList.contains("light-mode")) {
            localStorage.setItem("theme", "light");
            toggleBtn.innerText = "☀️ Light Mode";
        } else {
            localStorage.setItem("theme", "dark");
            toggleBtn.innerText = "🌙 Dark Mode";
        }
    });
}

// Add loading animation on page load
window.addEventListener("load", () => {
    const cards = document.querySelectorAll(".card");
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = "smooth";
