let lastAlert = "";

async function fetchData() {
    try {
        const response = await fetch("/data");
        const data = await response.json();

        // Access + alerts
        document.getElementById("access").innerText = data.access_status;
        document.getElementById("alert").innerText = data.alert;

        // Vitals
        document.getElementById("hr").innerText = data.heart_rate;
        document.getElementById("spo2").innerText = data.spo2;
        document.getElementById("temp").innerText = data.temperature;
        document.getElementById("risk").innerText = data.risk;

        // Profile
        document.getElementById("name").innerText = data.name;
        document.getElementById("age").innerText = data.age;
        document.getElementById("gender").innerText = data.gender;
        document.getElementById("smoking").innerText =
            data.smoking ? "Yes" : "No";
        document.getElementById("hypertension").innerText =
            data.hypertension ? "Yes" : "No";

        // Intruder redirect logic
     

    } catch (error) {
        console.log("Error fetching data", error);
    }
}

// Refresh every 2 seconds
setInterval(fetchData, 2000);
fetchData();

/* Dark mode toggle */
const toggleBtn = document.getElementById("themeToggle");

if (toggleBtn) {
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
}
