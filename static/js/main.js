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
    const rateLimitHint = document.getElementById("rate-limit-hint");

    const ICONS = {
        "user-plus": '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>',
        "map-pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
        "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
        "folder-plus": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/>',
        "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
        "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>'
    };

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

        if (message.toLowerCase().includes("rate limit") || message.toLowerCase().includes("403")) {
            rateLimitHint.style.display = "block";
        } else {
            rateLimitHint.style.display = "none";
        }
    }

    function hideError() {
        errorMsg.style.display = "none";
        rateLimitHint.style.display = "none";
    }

    function showResult(data) {
        const { session_id, profile, stats, insights } = data;

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

        // Render Insights
        renderInsights(insights);
    }

    function renderInsights(insights) {
        const insightsCard = document.getElementById("insights-card");
        const insightsList = document.getElementById("insights-list");

        if (!insights || insights.length === 0) {
            insightsCard.style.display = "none";
            return;
        }

        insightsList.innerHTML = "";
        
        // Calculate completeness score
        const issues = insights.filter(i => i.type !== 'success').length;
        const scoreValue = Math.max(20, Math.min(100, 100 - (issues * 15)));
        
        animateCounter("insights-score", scoreValue, "%");

        insights.forEach(insight => {
            const item = document.createElement("div");
            item.className = `insight-item ${insight.type}`;
            
            const iconPath = ICONS[insight.icon] || ICONS["info"];
            
            item.innerHTML = `
                <div class="insight-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${iconPath}
                    </svg>
                </div>
                <div class="insight-content">
                    <h4>${insight.title}</h4>
                    <p>${insight.message}</p>
                </div>
            `;
            insightsList.appendChild(item);
        });

        insightsCard.style.display = "block";
    }

    function animateCounter(elementId, target, suffix = "") {
        const el = document.getElementById(elementId);
        let current = 0;
        const duration = 1000;
        const increment = target / (duration / 16);

        function update() {
            current += increment;
            if (current >= target) {
                el.textContent = target + suffix;
                return;
            }
            el.textContent = Math.floor(current) + suffix;
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
