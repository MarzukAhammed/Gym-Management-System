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
    // 1. Elements dhora
    const cat = document.getElementById('floating-cat-container');
    const chatBox = document.getElementById('premium-chatbox');
    const userInput = document.getElementById('ai-user-input');
    const sendBtn = document.querySelector('.chat-input-area button');

    let isDragging = false;
    let offset = { x: 0, y: 0 };

    if (!cat || !chatBox) {
        console.error("Cat ba Chatbox container pawa jayni! HTML-e ID check korun.");
        return;
    }

    // --- DRAG LOGIC ---
    cat.addEventListener('mousedown', (e) => {
        isDragging = false; 
        offset.x = e.clientX - cat.getBoundingClientRect().left;
        offset.y = e.clientY - cat.getBoundingClientRect().top;
        
        function onMouseMove(e) {
            isDragging = true;
            cat.style.left = (e.clientX - offset.x) + 'px';
            cat.style.top = (e.clientY - offset.y) + 'px';
            cat.style.right = 'auto';
            cat.style.bottom = 'auto';
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', () => {
            document.removeEventListener('mousemove', onMouseMove);
        }, { once: true });
    });

    // --- CLICK & POSITION LOGIC ---
    cat.addEventListener('click', (e) => {
        if (!isDragging) {
            const rect = cat.getBoundingClientRect();
            const chatHeight = 450; 
            
            // Left alignment
            chatBox.style.left = (rect.left - 140) + "px";
            chatBox.style.right = "auto";

            // Smart Vertical logic (Screen boundary check)
            if (rect.top < chatHeight + 20) {
                chatBox.style.top = (rect.bottom + 10) + "px";
                chatBox.style.bottom = "auto";
            } else {
                chatBox.style.top = (rect.top - (chatHeight + 20)) + "px";
                chatBox.style.bottom = "auto";
            }

            toggleChat();
        }
    });

    // --- INPUT & SEND ---
    if (userInput) {
        userInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendToAI();
            }
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener("click", sendToAI);
    }
});

// --- HELPER FUNCTIONS (Outside DOMContentLoaded) ---

// 1. CSRF Token Function (Eta chara POST request fail korbe)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
    
    // User message bhashano
    messages.innerHTML += `
        <div class="message-wrapper user" style="justify-content: flex-end; display: flex; margin-bottom: 10px;">
            <div class="user-msg" style="background: #007bff; color: white; padding: 8px 15px; border-radius: 15px 15px 0 15px; max-width: 80%;">${msg}</div>
        </div>
    `;
    
    input.value = ""; 
    messages.scrollTop = messages.scrollHeight;

    console.log("Sending message to server...");

    fetch('/chat-with-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken') // CSRF Token pathano
        },
        body: `text=${encodeURIComponent(msg)}`
    })
    .then(res => {
        console.log("Response status:", res.status);
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
    })
    .then(data => {
        console.log("Data received:", data);
        if (data.reply) {
            messages.innerHTML += `
                <div class="message-wrapper bot" style="justify-content: flex-start; display: flex; margin-bottom: 10px;">
                    <div class="bot-msg" style="background: rgba(255, 255, 255, 0.2); color: white; padding: 8px 15px; border-radius: 15px 15px 15px 0; max-width: 80%;">${data.reply}</div>
                </div>
            `;
        }
        messages.scrollTop = messages.scrollHeight;
    })
    .catch(error => {
        console.error('Fetch error:', error);
        messages.innerHTML += `<div style="color: #ff4d4d; font-size: 12px; text-align: center;">Error: Lolona kotha bolte parchche na!</div>`;
    });
}