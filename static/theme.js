// Dark Mode Toggle Functionality
// Persists user preference in localStorage

function initDarkMode() {
    const themeToggle = document.getElementById('themeToggle');

    if (!themeToggle) return;

    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';

    // Apply the saved theme
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '☀️ Light Mode';
    } else {
        document.body.classList.remove('dark-mode');
        themeToggle.innerHTML = '🌙 Dark Mode';
    }

    // Toggle theme on button click
    themeToggle.addEventListener('click', () => {
        const isDark = document.body.classList.toggle('dark-mode');

        if (isDark) {
            themeToggle.innerHTML = '☀️ Light Mode';
            localStorage.setItem('theme', 'dark');
        } else {
            themeToggle.innerHTML = '🌙 Dark Mode';
            localStorage.setItem('theme', 'light');
        }
    });
}

// Initialize dark mode when page loads
document.addEventListener('DOMContentLoaded', initDarkMode);

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDarkMode);
} else {
    initDarkMode();
}
