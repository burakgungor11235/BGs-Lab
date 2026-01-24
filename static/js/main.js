/**
 * Main JavaScript functionality for BGsLab website
 * Includes: Reading Progress Bar, Theme Toggle, Code Copy, Footnote Preview, TOC Logic, Cookie Consent, KaTeX Rendering
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initReadingProgressBar();
    initThemeToggle();
    initCodeCopy();
    initFootnotePreview();
    initTOCLogic();
    initCookieConsent();
    initKaTeX();
});

/**
 * KaTeX Math Rendering
 */
function initKaTeX() {
    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false },
                { left: "\\[", right: "\\]", display: true },
            ],
            throwOnError: false,
        });
    }
}

/**
 * Reading Progress Bar functionality
 */
function initReadingProgressBar() {
    const progressBar = document.getElementById("progress-bar");
    if (progressBar) {
        function updateProgress() {
            const scrollTop = window.scrollY;
            const docHeight =
                document.documentElement.scrollHeight -
                document.documentElement.clientHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            // SECURITY FIX: Validate and bounds-check scroll percentage
            const safeScrollPercent = Math.max(0, Math.min(100, scrollPercent));
            progressBar.style.width = safeScrollPercent + "%";
        }

        window.addEventListener("scroll", updateProgress, { passive: true });
        updateProgress(); // Initial call
    }
}

/**
 * Theme Toggle Logic
 */
function initThemeToggle() {
    const toggleBtn = document.getElementById("theme-toggle");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const currentTheme =
                document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "light" ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
        });
    }
}

/**
 * Code Copy Logic
 */
function initCodeCopy() {
    document.querySelectorAll("pre").forEach((block) => {
        const code = block.querySelector("code");
        if (code) {
            const button = document.createElement("button");
            button.innerText = "Copy";
            button.className = "copy-btn";
            block.appendChild(button);

            button.addEventListener("click", async () => {
                await navigator.clipboard.writeText(code.innerText);
                button.innerText = "Copied";
                setTimeout(() => {
                    button.innerText = "Copy";
                }, 2000);
            });
        }
    });
}

/**
 * Footnote Hover Preview Logic
 */
function initFootnotePreview() {
    const refs = document.querySelectorAll(".footnote-reference a");
    if (refs.length === 0) return;

    const popover = document.createElement("div");
    popover.className = "footnote-popover";
    document.body.appendChild(popover);

    refs.forEach((ref) => {
        ref.addEventListener("mouseenter", function (e) {
            // Robust ID extraction from href (handles full URLs and hashes)
            const href = this.getAttribute("href");
            if (!href) return;

            const id = href.includes("#") ? href.split("#")[1] : null;
            if (!id) return;

            const footnote = document.getElementById(id);
            if (footnote) {
                const content = footnote.cloneNode(true);
                const backref = content.querySelector(".footnote-backref");
                if (backref) backref.remove();

                // Sanitize HTML
                popover.innerHTML = DOMPurify.sanitize(content.innerHTML, {
                    ALLOWED_TAGS: [
                        "p",
                        "a",
                        "em",
                        "strong",
                        "code",
                        "pre",
                        "sup",
                        "sub",
                        "br",
                        "span",
                    ],
                    ALLOWED_ATTR: ["href", "id", "class", "title"],
                    ALLOW_DATA_ATTR: false,
                    FORBID_ATTR: [
                        "onload",
                        "onerror",
                        "onclick",
                        "onmouseover",
                        "onstyle",
                    ],
                    FORBID_TAGS: [
                        "script",
                        "iframe",
                        "object",
                        "embed",
                        "form",
                        "input",
                    ],
                });
                popover.classList.add("visible");

                const rect = this.getBoundingClientRect();
                const popoverRect = popover.getBoundingClientRect();

                let left = rect.left + window.scrollX;
                let top = rect.bottom + window.scrollY + 10;

                // Keep popover on screen with bounds checking
                if (left + 300 > window.innerWidth) {
                    left = window.innerWidth - 320;
                }

                // Validate and bounds-check style assignments
                const safeLeft = Math.max(
                    0,
                    Math.min(window.innerWidth - 320, left),
                );
                const safeTop = Math.max(
                    0,
                    Math.min(window.innerHeight - 100, top),
                );

                popover.style.left = `${safeLeft}px`;
                popover.style.top = `${safeTop}px`;
            }
        });

        ref.addEventListener("mouseleave", function () {
            popover.classList.remove("visible");
        });
    });
}

/**
 * TOC Active State & Accordion Logic
 */
function initTOCLogic() {
    const tocLinks = document.querySelectorAll(".toc-list a");
    const sections = document.querySelectorAll(
        ".content-text h1, .content-text h2, .content-text h3",
    );

    if (tocLinks.length > 0 && sections.length > 0) {
        const observerOptions = {
            root: null,
            rootMargin: "-10% 0px -85% 0px",
            threshold: 0,
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    if (!id) return;

                    tocLinks.forEach((link) => link.classList.remove("active"));
                    document
                        .querySelectorAll(".toc-list li")
                        .forEach((li) => li.classList.remove("expanded"));

                    let activeLink = null;
                    try {
                        activeLink = document.querySelector(
                            `.toc-list a[href="#${CSS.escape(id)}"]`,
                        );
                        if (!activeLink) {
                            tocLinks.forEach((link) => {
                                const href = link.getAttribute("href");
                                if (href && href.endsWith(`#${id}`)) {
                                    activeLink = link;
                                }
                            });
                        }
                    } catch (e) {
                        console.warn("TOC Error: Invalid ID selector", id);
                    }

                    if (activeLink) {
                        activeLink.classList.add("active");
                        let parentLi = activeLink.closest("li");
                        while (parentLi) {
                            parentLi.classList.add("expanded");
                            parentLi = parentLi.parentElement.closest("li");
                        }
                    }
                }
            });
        }, observerOptions);

        sections.forEach((section) => {
            if (section.id) {
                observer.observe(section);
            }
        });
    }
}

/**
 * Cookie Consent Logic
 */
function initCookieConsent() {
    const CONSENT_KEY = "BGsLab_consent";

    function initConsent() {
        const banner = document.getElementById("cookie-consent");
        const consent = localStorage.getItem(CONSENT_KEY);
        if (!consent) {
            // SECURITY FIX: Add null check
            if (banner) banner.style.display = "flex";
        } else {
            const data = JSON.parse(consent);
            if (data.analytics) enableAnalytics();
        }
    }

    function loadUmami() {
        const script = document.createElement("script");
        script.defer = true;
        script.src = "https://cloud.umami.is/script.js";
        script.setAttribute(
            "data-website-id",
            "f5944805-c487-4a5a-ab0e-5cccaa1a6a5c",
        );
        document.head.appendChild(script);
    }

    function enableAnalytics() {
        loadUmami();
    }

    function saveConsent(analytics) {
        localStorage.setItem(
            CONSENT_KEY,
            JSON.stringify({
                analytics: analytics,
                timestamp: new Date().toISOString(),
            }),
        );
        // SECURITY FIX: Add null check
        const cookieBanner = document.getElementById("cookie-consent");
        if (cookieBanner) cookieBanner.style.display = "none";
        if (analytics) enableAnalytics();
    }

    // Set up event listeners
    const acceptBtn = document.getElementById("cookie-accept");
    const rejectBtn = document.getElementById("cookie-reject");

    if (acceptBtn) {
        acceptBtn.onclick = function () {
            saveConsent(true);
        };
    }

    if (rejectBtn) {
        rejectBtn.onclick = function () {
            saveConsent(false);
        };
    }

    // Initialize consent on load
    initConsent();
}