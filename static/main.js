// When the user scrolls the page, execute myFunction
window.onscroll = function() {scolling()};

function scolling() {
  var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
  var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  var scrolled = (winScroll / height) * 100;
  document.getElementById("myBar").style.width = scrolled + "%";
};

var offset = $(".navbar").height() + $(".header").height() + $("#collapsibleNavbar").height();

$('.navbar li a.anchor').click(function(event) {
    event.preventDefault();
    $($(this).attr('href'))[0].scrollIntoView();
    scrollBy(0, -offset);
});


$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});