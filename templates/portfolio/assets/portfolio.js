/**
 * Generated Portfolio Scripts
 * Handles charts, counting animations, and intersection observers.
 */

document.addEventListener("DOMContentLoaded", () => {
    // ---- Skills Chart (Chart.js) ----
    const ctx = document.getElementById('skills-chart');
    if (ctx && window.PORTFOLIO_DATA && window.PORTFOLIO_DATA.languages) {
        const langs = window.PORTFOLIO_DATA.languages;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: langs.map(l => l.name),
                datasets: [{
                    data: langs.map(l => l.percentage),
                    backgroundColor: langs.map(l => l.color),
                    borderWidth: 0,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        padding: 12,
                        backgroundColor: '#16162a',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 14 },
                        displayColors: true,
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1
                    }
                }
            }
        });
    }

    // ---- Intersection Observer for Skills Bar Animation ----
    const skillBars = document.querySelectorAll('.skill-bar-fill');
    const observerOptions = {
        threshold: 0.1
    };

    const skillObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.getAttribute('data-width');
                bar.style.width = width;
                skillObserver.unobserve(bar);
            }
        });
    }, observerOptions);

    skillBars.forEach(bar => skillObserver.observe(bar));

    // ---- Counter Animation for Stats ----
    const stats = document.querySelectorAll('.portfolio-stat-value');

    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count'));
                animateCounter(el, target);
                countObserver.unobserve(el);
            }
        });
    }, observerOptions);

    stats.forEach(stat => countObserver.observe(stat));

    function animateCounter(el, target) {
        if (target === 0) return;

        let current = 0;
        const duration = 1500;
        const stepTime = 16; // 60fps
        const totalSteps = duration / stepTime;
        const increment = target / totalSteps;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                el.textContent = target;
                clearInterval(timer);
            } else {
                el.textContent = Math.floor(current);
            }
        }, stepTime);
    }

    // ---- Fade-in Animation for Cards ----
    const projectCards = document.querySelectorAll('.project-card');
    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                fadeObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.05 });

    projectCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        fadeObserver.observe(card);
    });

    // Add CSS class dynamically for the fade animation
    const style = document.createElement('style');
    style.textContent = '.project-card.fade-in { opacity: 1 !important; transform: translateY(0) !important; }';
    document.head.appendChild(style);

    // ---- Smooth Scroll for internal links ----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
});
