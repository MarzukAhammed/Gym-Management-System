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
function toggleChat() {
    var container = document.getElementById('ai-chat-container');
    if (container) {
        container.classList.toggle('ai-chat-closed');
    }
}

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

function sendToAI() {
    const inputField = document.getElementById('ai-user-input');
    if (!inputField) return;
    
    const message = inputField.value.trim();
    if (!message) return;

    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML += `<div class="user-msg" style="text-align:right; margin: 10px 5px; color: #2563eb;"><b>You:</b> ${message}</div>`;
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
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        // Handle different possible key names from Django
        const reply = data.reply || data.message || "I'm processing that. One second...";
        
        chatMessages.innerHTML += `<div class="bot-msg" style="margin: 10px 5px; color: #059669;"><b>AI:</b> ${reply}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Redirect logic
        if (reply.includes("[REDIRECT:")) {
            const match = reply.match(/\[REDIRECT:(.*?)\]/);
            if (match) {
                setTimeout(() => { window.location.href = match[1]; }, 1500);
            }
        }
    })
    .catch(error => {
        console.error('AI Error:', error);
        chatMessages.innerHTML += `<div class="bot-msg" style="margin: 10px 5px; color: red;"><b>AI:</b> Connection snag. Try again!</div>`;
    });
}