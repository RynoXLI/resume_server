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
    const today = date.getTime();
    const anniversary = new Date(2019, 9, 12);

    const diffTime = Math.abs(date - anniversary);
    const diffYears = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 365));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24) - diffYears * 365);
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60) - (diffYears * 365 + diffDays)*24);
    const diffMins = Math.floor(diffTime / (1000 * 60) - (diffYears * 365 * 24 + diffDays * 24 + diffHours)*60);
    const diffSecs = Math.floor(diffTime / 1000 - (diffYears * 365 * 24 * 60 + diffDays * 24 * 60 + diffHours * 60 + diffMins)*60);

    let msg = "";
    let second = "seconds";
    let min = "minutes";
    let hour = "hours";
    let day = "days";
    let year = "years";

    if (diffSecs == 1) {
        second = "second";
    }
    if (diffMins == 1) {
        min = "minute";
    }
    if (diffHours == 1) {
        hour = "hour";
    }
    if (diffDays == 1) {
        day = 'day';
    }
    if (diffYears == 1) {
        year = 'year';
    }

    if (diffYears == 0 && diffDays == 0 && diffHours == 0 && diffMins == 0) {
        msg = diffSecs + " seconds";
    }
    else if (diffYears == 0 && diffDays == 0 && diffHours == 0){
        msg = diffMins + " " + min + " and " + diffSecs + " " + second;
    }
    else if (diffYears == 0 && diffDays == 0) {
        msg = diffHours + " " + hour + ", " + diffMins + " " + min + ", and " + diffSecs + " " + second;
    }
    else if (diffYears == 0) {
        msg = diffDays + " " + day + ", " + diffHours + " " + hour + ", " + diffMins + " " + min + ", and " + diffSecs + " " + second;
    }
    else {
        msg = diffYears + " " + year + ", " + diffDays + " " + day + ", " + diffHours + " " + hour + ", " + diffMins + " " + min + ", and " + diffSecs + " " + second;
    }


    $("#clock").text(msg);
//     console.log(diffYears + " years")
//    console.log(diffDays + " days");
//    console.log(diffHours + " hours");
//    console.log(diffMins + " minutes");
//    console.log(diffSecs + " seconds");
};

function getIPaddress() {
    $.ajax({
    url: "/ipaddress",
    type: "GET",
    dataType: 'json',
    success: function(res) {
        console.log(res);
        $('#ip').text(res['IP']);
    }});
}

function getStatus() {
    $.ajax({
    url: "/factoriostatus",
    type: "GET",
    dataType: 'json',
    success: function(res) {
        console.log(res);
        $('#status').text(res['status']);
    }});
}

function startFactorio() {
    $.ajax({
    url: "/startfactorio",
    type: "GET",
    dataType: 'json',
    success: function(res) {
        console.log(res);
        $('#status').text(res['status']);
    }});
}