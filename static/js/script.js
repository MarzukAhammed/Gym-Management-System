$('.one_slide').slick({
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows:false,
    dots:true
  });
$('.recon_main').slick({
    infinite: true,
    slidesToShow: 2,
    slidesToScroll: 2,
    arrows:false,
    dots:true,
  });
$('.brand_slider').slick({
    infinite: true,
    slidesToShow: 5,
    slidesToScroll: 2,
    arrows:true,
    dots:false,
    prevArrow:'<i class="fa-solid fa-angle-left prev_arrow"></i>',
    nextArrow:'<i class="fa-solid fa-angle-right next_arrow"></i>',

    
  });


  new VenoBox({
    selector: ".venobox"
});
$('.rating').starRating({
      starIconEmpty: 'far fa-star',
      starIconFull: 'fas fa-star',
      starColorEmpty: 'lightgray',
      starColorFull: '#FFC107',
      starsSize: 1, // em
      stars: 5,
      showInfo: false,
    });

    var mixer = mixitup('.class_down');



    $('.counter').counterUp({
      delay: 10,
      time: 1000
  });


  var navbar = document.getElementById("navbar");
  window.addEventListener("scroll",function(){
    navbar.classList.toggle("sticky",window.scrollY > 200);
  })

  var preloader = document.querySelector(".preloader");
  window.addEventListener("load",function(){
    preloader.classList.add("preloader_hide")
  })


  var btn = $('#button');

$(window).scroll(function() {
  if ($(window).scrollTop() > 300) {
    btn.addClass('show');
  } else {
    btn.removeClass('show');
  }
});

btn.on('click', function(e) {
  e.preventDefault();
  $('html, body').animate({scrollTop:0}, '300');
});


  var swiper = new Swiper('.mySwiper', {
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            loop: true,
        });