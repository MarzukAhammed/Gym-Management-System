/* --- SLIDERS & UI PLUGINS --- */
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

new VenoBox({
    selector: ".venobox"
});

$('.rating').starRating({
    starIconEmpty: 'far fa-star',
    starIconFull: 'fas fa-star',
    starColorEmpty: 'lightgray',
    starColorFull: '#FFC107',
    starsSize: 1,
    stars: 5,
    showInfo: false,
});

var mixer = mixitup('.class_down');

$('.counter').counterUp({
    delay: 10,
    time: 1000
});

/* --- NAVBAR & SCROLL --- */
var navbar = document.getElementById("navbar");
window.addEventListener("scroll", function () {
    if (navbar) {
        navbar.classList.toggle("sticky", window.scrollY > 200);
    }
});

var preloader = document.querySelector(".preloader");

// The standard way
window.addEventListener("load", function () {
    if (preloader) {
        preloader.classList.add("preloader_hide");
    }
});

// The Fail-safe: Force hide after 5 seconds if it's still stuck
setTimeout(function() {
    if (preloader && !preloader.classList.contains("preloader_hide")) {
        console.warn("Preloader forced to hide due to timeout.");
        preloader.classList.add("preloader_hide");
    }
}, 5000);

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

/* --- AI CHATBOT LOGIC --- */
/* --- AI CHATBOT LOGIC --- */
/* --- AI CHATBOT LOGIC --- */

/* --- AI CHATBOT LOGIC --- */

// 1. Toggle Open/Close
/* --- 1. THE MISSING PIECE: CSRF Utility --- */
/* --- 1. UTILS & SECURITY --- */
/**
 * Helper function to get Django CSRF Token
 */
document.addEventListener("DOMContentLoaded", function() {
    const cat = document.getElementById('floating-cat-container');
    const catImg = document.querySelector('#cat-trigger img') || document.getElementById('cat-trigger');
    
    const IDLE_PATH = "/static/cat_idle.gif"; 
    const RUN_PATH = "/static/images/cat_run.gif"; 

    let isDragging = false;
    let isMoving = false; 
    let startX, startY;
    let offset = { x: 0, y: 0 };
    let holdTimer;
    let isHolding = false;

    if (!cat) return;

    // --- MOUSE DOWN (Start) ---
    cat.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return; // Left click only
        
        isMoving = false;
        isHolding = false;
        isDragging = false;
        
        startX = e.clientX;
        startY = e.clientY;
        
        offset.x = e.clientX - cat.getBoundingClientRect().left;
        offset.y = e.clientY - cat.getBoundingClientRect().top;
        
        // Hold logic
        holdTimer = setTimeout(() => {
            if (!isMoving) {
                isHolding = true;
                if (typeof toggleChat === 'function') toggleChat();
            }
        }, 500);

        // 🆕 Sticky situation thamanor jonno mousemove ar mouseup window-te deya bhalo
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
        
        e.preventDefault(); // Browser default drag bondho kore
    });

    function onMouseMove(e) {
        const moveX = Math.abs(e.clientX - startX);
        const moveY = Math.abs(e.clientY - startY);

        if (moveX > 5 || moveY > 5) {
            isMoving = true; 
            isDragging = true;
            clearTimeout(holdTimer);
            
            cat.style.transition = 'none'; // Instant movement
            cat.style.position = 'fixed';
            cat.style.left = (e.clientX - offset.x) + 'px';
            cat.style.top = (e.clientY - offset.y) + 'px';
            cat.style.right = 'auto';
            cat.style.bottom = 'auto';
        }
    }

    function onMouseUp() {
        // 🆕 Window theke listener remove kora jate "sticky" na hoy
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        
        clearTimeout(holdTimer);
        cat.style.transition = 'all 0.5s ease'; // Back to smooth transition

        // Release the "stuck" state
        setTimeout(() => { 
            isDragging = false; 
        }, 100);
    }

    // --- CLICK LOGIC (Run Away) ---
    cat.addEventListener('click', (e) => {
        if (isMoving || isHolding) return; 

        if (typeof isLoggedIn !== 'undefined' && isLoggedIn === "false") {
            if (catImg) {
                catImg.src = RUN_PATH;
                catImg.onerror = function() {
                    this.src = IDLE_PATH;
                    this.onerror = null;
                };
            }

            const maxX = window.innerWidth - 150;
            const maxY = window.innerHeight - 150;
            const newX = Math.random() * maxX;
            const newY = Math.random() * maxY;

            cat.style.transform = newX < cat.offsetLeft ? "scaleX(-1)" : "scaleX(1)";
            cat.style.left = `${newX}px`;
            cat.style.top = `${newY}px`;

            setTimeout(() => { if (catImg) catImg.src = IDLE_PATH; }, 1000);
            return;
        }

        if (typeof toggleChat === 'function') toggleChat();
    });

    // --- AI EXTRACTION LOGIC ---
    window.sendToAI = function() {
        const input = document.getElementById('ai-user-input');
        if (!input || !input.value.trim()) return;

        fetch('/chat-with-ai/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCookie('csrftoken') },
            body: `text=${encodeURIComponent(input.value)}`
        })
        .then(res => res.json())
        .then(data => {
            const reply = data.reply;
            if (reply.toLowerCase().includes("breakfast") || reply.toLowerCase().includes("lunch") || reply.toLowerCase().includes("dinner")) {
                const extract = (meal) => {
                    const regex = new RegExp(`${meal}[\\s*:]+([^\\n\\r*#]+)`, 'i');
                    const match = reply.match(regex);
                    return match ? match[1].trim() : "Healthy Meal";
                };
                savePlanToAdmin("AI Personalized Plan", 2100, extract("Breakfast"), extract("Lunch"), extract("Dinner"));
            }
        });
    };
});// --- HELPER FUNCTIONS ---

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleChat() {
    const chatBox = document.getElementById('premium-chatbox');
    if (chatBox.style.display === "none" || chatBox.style.display === "") {
        chatBox.style.display = "flex";
        chatBox.style.animation = "fadeInUp 0.3s ease forwards";
    } else {
        chatBox.style.display = "none";
    }
}

function sendToAI() {
    const input = document.getElementById('ai-user-input');
    const messages = document.getElementById('chat-messages');

    if (!input || !input.value.trim()) return;

    const msg = input.value;

    messages.innerHTML += `
        <div class="message-wrapper user" style="justify-content: flex-end; display: flex; margin-bottom: 10px;">
            <div class="user-msg" style="background: #007bff; color: white; padding: 8px 15px; border-radius: 15px 15px 0 15px; max-width: 80%;">${msg}</div>
        </div>
    `;

    input.value = "";
    messages.scrollTop = messages.scrollHeight;

    // 🆕 BLOCK IF NOT LOGGED IN
    if (isLoggedIn === "false") {
        messages.innerHTML += `
        <div class="message-wrapper bot" style="justify-content:flex-start;display:flex;margin-bottom:10px;">
            <div class="bot-msg" style="background:#ff4d4d;color:white;padding:8px 15px;border-radius:15px;">
                😾 Login koro age!
            </div>
        </div>`;
        return;
    }

    fetch('/chat-with-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `text=${encodeURIComponent(msg)}`
    })
    .then(res => res.json())
    .then(data => {
        messages.innerHTML += `
            <div class="message-wrapper bot" style="justify-content: flex-start; display: flex; margin-bottom: 10px;">
                <div class="bot-msg" style="background: rgba(255,255,255,0.2); color: white; padding: 8px 15px; border-radius: 15px;">${data.reply}</div>
            </div>
        `;
        messages.scrollTop = messages.scrollHeight;

        const replyLower = data.reply.toLowerCase();

        // 🆕 DELETE LOGIC: Jodi message-e "delete" ar "plan" thake
        if (replyLower.includes("delete") && replyLower.includes("plan")) {
            deletePlanFromAdmin();
        }
        // 🆕 DIET PLAN TRIGGER: AI message-e "diet plan" thakle details extract kore save korbe
        else if (replyLower.includes("diet plan") || replyLower.includes("breakfast")) {
            // Extraction Logic: AI reply theke Breakfast, Lunch, Dinner er line gulo alada kora
            const lines = data.reply.split('\n');
            let bf = "Healthy Meal", ln = "Healthy Meal", dn = "Healthy Meal";
            
            lines.forEach(line => {
                if (line.toLowerCase().includes("breakfast")) bf = line.trim();
                if (line.toLowerCase().includes("lunch")) ln = line.trim();
                if (line.toLowerCase().includes("dinner")) dn = line.trim();
            });

            savePlanToAdmin("AI Personalized Plan", 2100, bf, ln, dn);
        }
    });
}

// 🆕 UPDATED: Details soho save kora
function savePlanToAdmin(planTitle, planCalories, bf, ln, dn) {
    fetch('/save-diet-plan-ai/', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            title: planTitle,
            calories: planCalories,
            breakfast: bf, 
            lunch: ln,
            dinner: dn 
        })
    })
    .then(response => response.json())
    .then(data => {
        const messages = document.getElementById('chat-messages');
        if (messages) {
            messages.innerHTML += `
            <div class="message-wrapper bot" style="justify-content: flex-start; display: flex; margin-bottom: 10px;">
                <div class="bot-msg" style="background: #28a745; color: white; padding: 8px 15px; border-radius: 15px;">
                    ✅ Bhai, food names soho plan-ta save kore diyechi!
                </div>
            </div>`;
            messages.scrollTop = messages.scrollHeight;
        }
    });
}

// 🆕 NEW FEATURE: Delete Plan Function
function deletePlanFromAdmin() {
    fetch('/delete-diet-plan-ai/', { // Apnar urls.py te ei path-ta thakte hobe
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        const messages = document.getElementById('chat-messages');
        if (messages) {
            messages.innerHTML += `
            <div class="message-wrapper bot" style="justify-content: flex-start; display: flex; margin-bottom: 10px;">
                <div class="bot-msg" style="background: #dc3545; color: white; padding: 8px 15px; border-radius: 15px;">
                    🗑️ Bhai, puran plan-ta delete kore diyechi!
                </div>
            </div>`;
            messages.scrollTop = messages.scrollHeight;
        }
    });
}