/**
 * GitHub Portfolio Generator - Main JavaScript
 * Handles form submission, loading states, and UI interactions.
 */

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("generate-form");
    const usernameInput = document.getElementById("username-input");
    const generateBtn = document.getElementById("generate-btn");
    const btnText = generateBtn.querySelector(".btn-text");
    const btnLoader = generateBtn.querySelector(".btn-loader");
    const errorMsg = document.getElementById("error-msg");
    const selectedTheme = document.getElementById("selected-theme");
    const resultSection = document.getElementById("result");
    const regenerateBtn = document.getElementById("regenerate-btn");

    // ---- Theme Selection ----
    document.querySelectorAll(".theme-pill").forEach((pill) => {
        pill.addEventListener("click", () => {
            document.querySelectorAll(".theme-pill").forEach((p) => p.classList.remove("active"));
            pill.classList.add("active");
            selectedTheme.value = pill.dataset.theme;
        });
    });

    // Theme cards in the themes section also act as selectors
    document.querySelectorAll(".theme-card").forEach((card) => {
        card.addEventListener("click", () => {
            const themeId = card.dataset.theme;
            selectedTheme.value = themeId;

            // Update pills
            document.querySelectorAll(".theme-pill").forEach((p) => p.classList.remove("active"));
            const targetPill = document.querySelector(`.theme-pill[data-theme="${themeId}"]`);
            if (targetPill) targetPill.classList.add("active");

            // Scroll to generator
            document.getElementById("generator").scrollIntoView({ behavior: "smooth" });
        });
    });

    // ---- Form Submission ----
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = usernameInput.value.trim();
        if (!username) {
            showError("Please enter a GitHub username.");
            return;
        }

        // Validate username format
        if (!/^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$/.test(username)) {
            showError("Invalid GitHub username format. Usernames can only contain alphanumeric characters and hyphens.");
            return;
        }

        setLoading(true);
        hideError();

        try {
            const response = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username,
                    theme: selectedTheme.value,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to generate portfolio.");
            }

            // Show result section
            showResult(data);
        } catch (err) {
            showError(err.message || "Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    });

    // ---- Regenerate ----
    if (regenerateBtn) {
        regenerateBtn.addEventListener("click", () => {
            resultSection.style.display = "none";
            usernameInput.focus();
            window.scrollTo({
                top: document.getElementById("generator").offsetTop - 80,
                behavior: "smooth",
            });
        });
    }

    // ---- Helper Functions ----
    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        btnText.style.display = isLoading ? "none" : "inline-flex";
        btnLoader.style.display = isLoading ? "inline-flex" : "none";
        if (isLoading) {
            generateBtn.style.opacity = "0.8";
            generateBtn.style.cursor = "wait";
        } else {
            generateBtn.style.opacity = "1";
            generateBtn.style.cursor = "pointer";
        }
    }

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.style.display = "block";
    }

    function hideError() {
        errorMsg.style.display = "none";
    }

    function showResult(data) {
        const { session_id, profile, stats } = data;

        // Populate result card
        document.getElementById("result-avatar").src = profile.avatar_url;
        document.getElementById("result-name").textContent = profile.name;
        document.getElementById("result-username").textContent = `@${profile.username}`;
        document.getElementById("result-repos").textContent = stats.total_repos;
        document.getElementById("result-stars").textContent = stats.total_stars;
        document.getElementById("result-forks").textContent = stats.total_forks;

        // Set links
        document.getElementById("preview-link").href = `/preview/${session_id}/`;
        document.getElementById("download-link").href = `/download/${session_id}`;

        // Show result section with animation
        resultSection.style.display = "block";
        resultSection.scrollIntoView({ behavior: "smooth", block: "center" });

        // Animate numbers counting up
        animateCounter("result-repos", stats.total_repos);
        animateCounter("result-stars", stats.total_stars);
        animateCounter("result-forks", stats.total_forks);
    }

    function animateCounter(elementId, target) {
        const el = document.getElementById(elementId);
        let current = 0;
        const duration = 1000;
        const increment = target / (duration / 16);

        function update() {
            current += increment;
            if (current >= target) {
                el.textContent = target;
                return;
            }
            el.textContent = Math.floor(current);
            requestAnimationFrame(update);
        }

        if (target > 0) {
            update();
        }
    }

    // ---- Smooth scroll for nav links ----
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (e) {
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    // ---- Navbar scroll effect ----
    let lastScroll = 0;
    window.addEventListener("scroll", () => {
        const navbar = document.querySelector(".navbar");
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.style.background = "rgba(6, 6, 15, 0.95)";
        } else {
            navbar.style.background = "rgba(6, 6, 15, 0.8)";
        }

        lastScroll = currentScroll;
    });
});
