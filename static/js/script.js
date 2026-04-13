let isDeleting = false;

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
    const chatBox = document.getElementById('premium-chatbox');
    const userInput = document.getElementById('ai-user-input');
    const sendBtn = document.querySelector('.chat-input-area button');

    const IDLE_PATH = catImg ? catImg.src : "";
    const RUN_PATH = catImg ? catImg.src : "";

    let isDragging = false;
    let isMoving = false;
    let startX, startY;
    let offset = { x: 0, y: 0 };

    if (!cat || !chatBox) return;

    // --- DRAG LOGIC ---
    cat.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return; 

        isDragging = false; 
        isMoving = false;
        startX = e.clientX;
        startY = e.clientY;

        offset.x = e.clientX - cat.getBoundingClientRect().left;
        offset.y = e.clientY - cat.getBoundingClientRect().top;
        
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
        e.preventDefault(); 
    });

    function onMouseMove(e) {
        const moveX = Math.abs(e.clientX - startX);
        const moveY = Math.abs(e.clientY - startY);

        if (moveX > 5 || moveY > 5) {
            isDragging = true;
            isMoving = true;
            cat.style.transition = 'none'; 
            cat.style.left = (e.clientX - offset.x) + 'px';
            cat.style.top = (e.clientY - offset.y) + 'px';
            cat.style.right = 'auto';
            cat.style.bottom = 'auto';
        }
    }

    function onMouseUp() {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        cat.style.transition = 'all 0.3s ease';
        setTimeout(() => { isDragging = false; isMoving = false; }, 100);
    }

    // --- CLICK LOGIC ---
    cat.addEventListener('click', (e) => {
        if (isMoving || isDragging) return;

        if (typeof isLoggedIn !== 'undefined' && isLoggedIn === "false") {
            if (catImg) {
                catImg.src = RUN_PATH + "?" + Date.now();
            }

            const maxX = window.innerWidth - 200;
            const maxY = window.innerHeight - 200;

            const newX = Math.random() * maxX;
            const newY = Math.random() * maxY;

            cat.style.left = `${newX}px`;
            cat.style.top = `${newY}px`;

            setTimeout(() => {
                if (catImg) catImg.src = IDLE_PATH;
            }, 800);

            return;
        }

        const rect = cat.getBoundingClientRect();
        const chatWidth = 320;
        const chatHeight = 450;
        const screenWidth = window.innerWidth;

        let targetLeft = rect.left - (chatWidth / 2) + (rect.width / 2);
        let targetTop = rect.top - chatHeight - 20;

        if (targetLeft < 10) targetLeft = 10;
        if (targetLeft + chatWidth > screenWidth) targetLeft = screenWidth - chatWidth - 10;

        if (targetTop < 10) {
            targetTop = rect.bottom + 20;
        }

        chatBox.style.left = `${targetLeft}px`;
        chatBox.style.top = `${targetTop}px`;

        toggleChat();
    });

    // --- INPUT ---
    if (userInput) {
        userInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") { e.preventDefault(); sendToAI(); }
        });
    }

    if (sendBtn) sendBtn.addEventListener("click", sendToAI);
});


// --- HELPER FUNCTIONS ---

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
    }
    return cookieValue;
}

function toggleChat() {
    const chatBox = document.getElementById('premium-chatbox');
    chatBox.style.display = (chatBox.style.display === "flex") ? "none" : "flex";
}


// --- 🧠 USER CONTEXT ---
function getUserContext() {
    const el = document.getElementById("global-user-context");
    if (!el) return {};
    return {
        username: el.dataset.username,
        weight: el.dataset.weight,
        height: el.dataset.height
    };
}

function hasDeletePlanIntent(text) {
    return /(delete|remove|clear)\b/.test(text) && /(diet|meal)?\s*plan\b|diet\b|meal\b/.test(text);
}

function hasCreatePlanIntent(text) {
    const createVerb = /(create|make|generate|give|add|save|build|prepare)\b/.test(text);
    const mentionsDiet = /((diet|meal)\s*plan\b|\bdiet\b|\bmeal\b)/.test(text);
    const asksAnother = /(another|new one|new plan)\b/.test(text);
    return (createVerb && mentionsDiet) || (createVerb && asksAnother);
}

function extractDietPlanFromReply(reply) {
    if (!reply) return null;

    const normalized = reply.replace(/\r/g, "");
    const caloriesMatch = normalized.match(/calories?\s*[:\-]\s*(\d{3,5})/i);
    const breakfastMatch = normalized.match(/breakfast\s*[:\-]\s*([^\n]+)/i);
    const lunchMatch = normalized.match(/lunch\s*[:\-]\s*([^\n]+)/i);
    const dinnerMatch = normalized.match(/dinner\s*[:\-]\s*([^\n]+)/i);
    const titleMatch = normalized.match(/(?:title|plan)\s*[:\-]\s*([^\n]+)/i);

    if (!breakfastMatch || !lunchMatch || !dinnerMatch) {
        return null;
    }

    return {
        title: (titleMatch && titleMatch[1] ? titleMatch[1].trim() : "AI Diet Plan"),
        calories: caloriesMatch ? parseInt(caloriesMatch[1], 10) : 2000,
        breakfast: breakfastMatch[1].trim(),
        lunch: lunchMatch[1].trim(),
        dinner: dinnerMatch[1].trim()
    };
}

function buildFallbackPlanFromUserMessage(userMsgLower) {
    if (userMsgLower.includes("vegan")) {
        return {
            title: "Vegan Diet Plan",
            calories: 2000,
            breakfast: "Overnight oats with almond milk, chia seeds, banana, and walnuts",
            lunch: "Chickpea quinoa bowl with spinach, cucumber, tomato, and olive oil dressing",
            dinner: "Tofu stir-fry with mixed vegetables and brown rice"
        };
    }

    if (userMsgLower.includes("vegetarian")) {
        return {
            title: "Vegetarian Diet Plan",
            calories: 2100,
            breakfast: "Greek yogurt, mixed berries, oats, and honey",
            lunch: "Paneer and vegetable wrap with side salad",
            dinner: "Lentil soup with whole-grain roti and sauteed vegetables"
        };
    }

    return {
        title: "AI Diet Plan",
        calories: 2000,
        breakfast: "Egg whites or tofu scramble, oats, and fruit",
        lunch: "Lean protein or legumes, brown rice, and mixed vegetables",
        dinner: "Grilled protein or beans, salad, and sweet potato"
    };
}


// --- 🧠 AI SEND ---
function sendToAI() {
    const input = document.getElementById('ai-user-input');
    const messages = document.getElementById('chat-messages');
    if (!input || !input.value.trim()) return;

    const userMsg = input.value;
    const userMsgLower = userMsg.toLowerCase();
    const wantsPlanCreation = hasCreatePlanIntent(userMsgLower);

    // Command: delete existing diet plans
    if (hasDeletePlanIntent(userMsgLower)) {
        messages.innerHTML += `<div class="message-wrapper user" style="justify-content: flex-end; display: flex; margin-bottom: 10px;"><div class="user-msg" style="background: #007bff; color: white; padding: 8px 15px; border-radius: 15px;">${userMsg}</div></div>`;
        input.value = "";
        deleteDietPlan();
        return;
    }

    // Normal AI Chat Logic...
    messages.innerHTML += `<div class="message-wrapper user" style="justify-content: flex-end; display: flex; margin-bottom: 10px;"><div class="user-msg" style="background: #007bff; color: white; padding: 8px 15px; border-radius: 15px;">${userMsg}</div></div>`;
    input.value = "";

    // Context from your hidden div
    const ctx = document.getElementById('global-user-context');
    let profileData = ctx ? ` [Context: Weight=${ctx.dataset.weight}, Height=${ctx.dataset.height}]` : "";

    const structuredPlanInstruction = wantsPlanCreation
        ? " Return ONLY this format in plain text: Title: ...\\nCalories: ...\\nBreakfast: ...\\nLunch: ...\\nDinner: ..."
        : "";

    fetch('/chat-with-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken') || (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '')
        },
        body: `text=${encodeURIComponent(userMsg + " " + profileData + structuredPlanInstruction)}`
    })
    .then(res => res.json())
    .then(data => {
        messages.innerHTML += `<div class="message-wrapper bot" style="justify-content: flex-start; display: flex; margin-bottom: 10px;"><div class="bot-msg" style="background: rgba(255,255,255,0.2); color: white; padding: 8px 15px; border-radius: 15px;">${data.reply}</div></div>`;
        
        // Auto-save generated diet plans when request intent + response format match
        if (!isDeleting) {
            const parsedPlan = extractDietPlanFromReply(data.reply || "");
            if (wantsPlanCreation && parsedPlan) {
                savePlanToAdmin(
                    parsedPlan.title,
                    parsedPlan.calories,
                    parsedPlan.breakfast,
                    parsedPlan.lunch,
                    parsedPlan.dinner
                ).then((saveRes) => {
                    if (saveRes && saveRes.status === "success") {
                        messages.innerHTML += `<div style="color:#6dff8b; text-align:center; font-size:13px; margin:5px 0;">✅ Diet plan saved!</div>`;
                    } else {
                        messages.innerHTML += `<div style="color:#ff8a8a; text-align:center; font-size:13px; margin:5px 0;">❌ Could not save diet plan. ${saveRes && saveRes.message ? saveRes.message : ""}</div>`;
                    }
                    messages.scrollTop = messages.scrollHeight;
                }).catch(() => {
                    messages.innerHTML += `<div style="color:#ff8a8a; text-align:center; font-size:13px; margin:5px 0;">❌ Could not save diet plan due to network/server error.</div>`;
                    messages.scrollTop = messages.scrollHeight;
                });
            } else if (wantsPlanCreation && !parsedPlan) {
                const fallbackPlan = buildFallbackPlanFromUserMessage(userMsgLower);
                savePlanToAdmin(
                    fallbackPlan.title,
                    fallbackPlan.calories,
                    fallbackPlan.breakfast,
                    fallbackPlan.lunch,
                    fallbackPlan.dinner
                ).then((saveRes) => {
                    if (saveRes && saveRes.status === "success") {
                        messages.innerHTML += `<div style="color:#6dff8b; text-align:center; font-size:13px; margin:5px 0;">✅ Plan saved from request context (fallback mode).</div>`;
                    } else {
                        messages.innerHTML += `<div style="color:#ff8a8a; text-align:center; font-size:13px; margin:5px 0;">❌ Fallback plan could not be saved. ${saveRes && saveRes.message ? saveRes.message : ""}</div>`;
                    }
                    messages.scrollTop = messages.scrollHeight;
                }).catch(() => {
                    messages.innerHTML += `<div style="color:#ff8a8a; text-align:center; font-size:13px; margin:5px 0;">❌ Fallback save failed due to network/server error.</div>`;
                    messages.scrollTop = messages.scrollHeight;
                });
            }
        }
        messages.scrollTop = messages.scrollHeight;
    });
}

// --- SAVE ---
function savePlanToAdmin(title, cals, bf, ln, dn) {
    return fetch('/save-diet-plan-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ title, calories: cals, breakfast: bf, lunch: ln, dinner: dn })
    }).then(res => res.json());
}


// --- DELETE ---

function deleteDietPlan() {
    // 1. Flag true kora jate auto-save bondho hoy
    isDeleting = true; 

    fetch('/delete-diet-plan-ai/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') || (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : ''),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        const messages = document.getElementById('chat-messages');
        if (data.status === 'success') {
            messages.innerHTML += `<div style="color: #ff4d4d; text-align: center; font-size: 13px; margin: 5px 0;">🗑️ ${data.message || 'Plan has been deleted!'}</div>`;
        } else if (data.status === 'no_plan') {
            messages.innerHTML += `<div style="color: #ffd166; text-align: center; font-size: 13px; margin: 5px 0;">⚠️ ${data.message || 'No saved diet plan found.'}</div>`;
        } else if (data.status === 'error') {
            messages.innerHTML += `<div style="color: #ff8a8a; text-align: center; font-size: 13px; margin: 5px 0;">❌ ${data.message || 'Could not delete plan.'}</div>`;
        } else {
            messages.innerHTML += `<div style="color: #ffd166; text-align: center; font-size: 13px; margin: 5px 0;">⚠️ Unexpected delete response.</div>`;
        }
        messages.scrollTop = messages.scrollHeight;
        
        // 2. Kichu somoy por flag reset (Safe boundary)
        setTimeout(() => { isDeleting = false; }, 3000);
    })
    .catch(err => {
        console.error("Delete Error:", err);
        isDeleting = false;
    });
}