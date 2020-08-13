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

function setAnniversary() {
    const date = new Date();
    console.log(date.getTimezoneOffset());
    const today = date.getTime();
    const anniversary = new Date(2019, 10, 12);

    const diffTime = Math.abs(date - anniversary);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60) - diffDays * 24);
    const diffMins = Math.floor(diffTime / (1000 * 60) - (diffDays * 24 * 60 + diffHours * 60));
    const diffSecs = Math.floor(diffTime / 1000 - (diffDays * 24 * 60 * 60 + diffHours * 60 * 60 + diffMins * 60));

    $("#clock").text(diffDays + " days, " + diffHours + " hours, " + diffMins + " minutes, and " + diffSecs + " seconds" );
//    console.log(diffDays + " days");
//    console.log(diffHours + " hours");
//    console.log(diffMins + " minutes");
//    console.log(diffSecs + " seconds");
};