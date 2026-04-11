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

/* --- 2. CAT BRAIN (STATE MACHINE) --- */
let sleepTimer;

function setCatState(state) {
    const cat = document.getElementById('cat-pet');
    if (!cat) return;
    
    cat.setAttribute('data-state', state);
    
    // Clean all possible animation classes to prevent stacking bugs
    cat.classList.remove('animate__pulse', 'animate__bounceIn', 'animate__infinite', 'animate__shakeX');
    
    if (state === 'pointing') {
        cat.classList.add('animate__bounceIn');
    } else if (state === 'idle') {
        cat.classList.add('animate__pulse', 'animate__infinite');
    } else if (state === 'sleeping') {
        // We let the CSS handle the 'closed eyes' look via the data-state
        cat.classList.add('animate__pulse'); 
    }
}

function startSleepTimer() {
    clearTimeout(sleepTimer);
    // 30 seconds of inactivity = cat falls asleep
    sleepTimer = setTimeout(() => {
        const container = document.getElementById('ai-chat-container');
        if (container && container.classList.contains('ai-chat-closed')) {
            setCatState('sleeping');
        }
    }, 30000); 
}

/* --- 3. UI TOGGLE --- */
function toggleChat() {
    const container = document.getElementById('ai-chat-container');
    if (!container) return;

    const isOpening = container.classList.contains('ai-chat-closed');
    container.classList.toggle('ai-chat-closed');

    if (isOpening) {
        // Cat points to the box when it opens
        clearTimeout(sleepTimer);
        setCatState('pointing');
        
        // After 2 seconds, cat looks back at the user
        setTimeout(() => {
            if (!container.classList.contains('ai-chat-closed')) {
                setCatState('idle');
            }
        }, 2000);
    } else {
        // Cat becomes idle and starts the sleep countdown
        setCatState('idle');
        startSleepTimer();
    }
}

/* --- 4. DRAG & INITIALIZATION --- */
document.addEventListener("DOMContentLoaded", function() {
    const container = document.getElementById("ai-chat-container");
    const catHead = document.getElementById("cat-pet");
    const inputField = document.getElementById('ai-user-input');

    if (!container || !catHead) return;

    startSleepTimer(); // Initialize cat sleep logic

    let isDragging = false;
    let startX, startY;

    catHead.addEventListener("mousedown", (e) => {
        if (e.target.tagName === 'BUTTON') return;

        isDragging = false; 
        const rect = container.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;

        function onMouseMove(e) {
            isDragging = true;
            container.style.position = "fixed";
            container.style.left = (e.clientX - startX) + "px";
            container.style.top = (e.clientY - startY) + "px";
            container.style.bottom = "auto";
            container.style.right = "auto";
        }

        function onMouseUp() {
            document.removeEventListener("mousemove", onMouseMove);
            document.removeEventListener("mouseup", onMouseUp);
            if (!isDragging) toggleChat();
        }

        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
    });

    if (inputField) {
        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendToAI();
        });
    }
});

/* --- 5. CHAT LOGIC --- */
function sendToAI() {
    const inputField = document.getElementById('ai-user-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (!inputField || !chatMessages) return;
    
    const message = inputField.value.trim();
    if (!message) return;

    // Add User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'user-msg animate__animated animate__fadeInRight animate__faster';
    userDiv.innerHTML = `<b>You:</b> ${message}`;
    chatMessages.appendChild(userDiv);
    
    inputField.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    fetch('/chat-with-ai/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `text=${encodeURIComponent(message)}`
    })
    .then(response => {
        if (!response.ok) throw new Error('Status: ' + response.status);
        return response.json();
    })
    .then(data => {
        const reply = data.reply || data.message || "Meow!";
        const botDiv = document.createElement('div');
        botDiv.className = 'bot-msg animate__animated animate__fadeInLeft animate__faster';
        botDiv.innerHTML = `<b>Lolona:</b> ${reply}`;
        chatMessages.appendChild(botDiv);
        
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    })
    .catch(error => {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bot-msg animate__animated animate__shakeX';
        errorDiv.style.color = "#ef4444";
        errorDiv.innerHTML = `<b>System:</b> Connection snag.`;
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}