// --- PRELOADER MUST RUN FIRST ---
(function () {
    const preloader = document.querySelector(".preloader");
    if (!preloader) return;

    function hidePreloader() {
        preloader.classList.add("preloader_hide");
        setTimeout(function () {
            try { preloader.remove(); } catch (e) {}
        }, 700);
    }

    window.addEventListener("load", hidePreloader);
    // Fail-safe: force hide even if some JS/plugin breaks.
    setTimeout(function () {
        if (!preloader.classList.contains("preloader_hide")) hidePreloader();
    }, 3500);
})();

let isDeleting = false;

/* --- SLIDERS & UI PLUGINS --- */
try {
    if (window.jQuery) {
        // Slick sliders (guarded)
        if (jQuery.isFunction(jQuery.fn.slick)) {
            $('.one_slide').slick({
                infinite: true,
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: false,
                dots: true
            });

            $('.recon_main').slick({
                infinite: true,
                slidesToShow: 2,
                slidesToScroll: 2,
                arrows: false,
                dots: true,
            });

            $('.brand_slider').slick({
                infinite: true,
                slidesToShow: 5,
                slidesToScroll: 2,
                arrows: true,
                dots: false,
                prevArrow: '<i class="fa-solid fa-angle-left prev_arrow"></i>',
                nextArrow: '<i class="fa-solid fa-angle-right next_arrow"></i>',
            });
        } else {
            console.warn("Slick not loaded. Skipping sliders.");
        }

        // Star rating (guarded)
        if (jQuery.isFunction(jQuery.fn.starRating)) {
            $('.rating').starRating({
                starIconEmpty: 'far fa-star',
                starIconFull: 'fas fa-star',
                starColorEmpty: 'lightgray',
                starColorFull: '#FFC107',
                starsSize: 1,
                stars: 5,
                showInfo: false,
            });
        }

        // Counter up (guarded)
        if (jQuery.isFunction(jQuery.fn.counterUp)) {
            $('.counter').counterUp({
                delay: 10,
                time: 1000
            });
        }
    }

    // MixItUp (guarded) - keep for old grid
    if (typeof mixitup === "function") {
        if (document.querySelector(".class_down")) {
            mixitup('.class_down');
        }
        // NOTE: .challenge_grid is handled in index.html to ensure current-day filtering.
    }

    // VenoBox (guarded)
    if (typeof VenoBox === "function") {
        new VenoBox({ selector: ".venobox" });
    }
} catch (e) {
    console.warn("UI plugins init error:", e);
}

/* --- LIVE DHAKA TIMER (365-day cycle) --- */
(function () {
    const daysEl = document.getElementById("dhakaDaysPassed");
    const hoursEl = document.getElementById("dhakaHours");
    const minutesEl = document.getElementById("dhakaMinutes");
    const secondsEl = document.getElementById("dhakaSeconds");
    const liveEl = document.getElementById("dhakaLiveTime");
    if (!daysEl || !hoursEl || !minutesEl || !secondsEl || !liveEl) return;

    const startIso = daysEl.getAttribute("data-cycle-start") || "";
    const cycleStart = startIso ? new Date(startIso) : new Date();
    const cycleMs = 365 * 24 * 60 * 60 * 1000;

    const clockFmt12 = new Intl.DateTimeFormat("en-US", {
        timeZone: "Asia/Dhaka",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
    });

    const partsFmt = new Intl.DateTimeFormat("en-US", {
        timeZone: "Asia/Dhaka",
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
    });

    const dateTimeFmt = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Asia/Dhaka",
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
    });

    function tick() {
        const now = new Date();
        const elapsed = Math.max(0, now.getTime() - cycleStart.getTime());
        // Cap at 365 days so it behaves like a "year cycle" timer.
        const within = Math.min(elapsed, cycleMs);

        const totalSeconds = Math.floor(within / 1000);
        const days = Math.floor(totalSeconds / 86400);

        daysEl.textContent = String(days);
        // Current Dhaka clock components (12-hour)
        const parts = partsFmt.formatToParts(now);
        const dhakaHour = parts.find(p => p.type === "hour")?.value || "--";
        const dhakaMinute = parts.find(p => p.type === "minute")?.value || "--";
        const dhakaSecond = parts.find(p => p.type === "second")?.value || "--";
        hoursEl.textContent = String(dhakaHour);
        minutesEl.textContent = String(dhakaMinute);
        secondsEl.textContent = String(dhakaSecond);

        // "Nanosecond" display (browser only gives ms; show ms live)
        liveEl.textContent = String(now.getMilliseconds()).padStart(3, "0");
        // Tooltip: full Dhaka time
        liveEl.setAttribute("title", dateTimeFmt.format(now) + " (Asia/Dhaka)");
        // Also show Dhaka time like 12.03 in the title (12-hour)
        liveEl.setAttribute("data-dhaka-time", clockFmt12.format(now).replace(":", "."));
    }

    tick();
    setInterval(tick, 50);
})();

/* --- NAVBAR & SCROLL --- */
var navbar = document.getElementById("navbar");
window.addEventListener("scroll", function () {
    if (navbar) {
        navbar.classList.toggle("sticky", window.scrollY > 200);
    }
});

// Preloader logic handled at top of file.

var btn = $('#button');
$(window).scroll(function () {
    if ($(window).scrollTop() > 300) {
        btn.addClass('show');
    } else {
        btn.removeClass('show');
    }
});

btn.on('click', function (e) {
    e.preventDefault();
    $('html, body').animate({ scrollTop: 0 }, '300');
});

/* --- ERROR-PRONE PLUGINS (Wrapped in Safety Checks) --- */
$(document).ready(function () {
    if ($.isFunction($.fn.justFlipIt)) {
        $(".flip-card").justFlipIt({
            FlipType: 'click'
        });
    } else {
        console.warn("justFlipIt plugin failed to load. Skipping...");
    }
});

/* --- AI CHATBOT LOGIC IS NOW MANAGED IN templates/chatbox_partial.html FOR CONSISTENCY --- */
/* --- END OF SCRIPT --- */