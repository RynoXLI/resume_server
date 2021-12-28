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
    // const date = new Date();
    // const today = date.getTime();
    // const anniversary = new Date(2019, 9, 12);

    // const diffTime = Math.abs(date - anniversary);
    // const diffYears = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 365));
    // const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24) - diffYears * 365);
    // const diffHours = Math.floor(diffTime / (1000 * 60 * 60) - (diffYears * 365 + diffDays)*24);
    // const diffMins = Math.floor(diffTime / (1000 * 60) - (diffYears * 365 * 24 + diffDays * 24 + diffHours)*60);
    // const diffSecs = Math.floor(diffTime / 1000 - (diffYears * 365 * 24 * 60 + diffDays * 24 * 60 + diffHours * 60 + diffMins)*60);

    // console.log
    // let msg = "";
    // let second = "seconds";
    // let min = "minutes";
    // let hour = "hours";
    // let day = "days";
    // let year = "years";

    // if (diffSecs == 1) {
    //     second = "second";
    // }
    // if (diffMins == 1) {
    //     min = "minute";
    // }
    // if (diffHours == 1) {
    //     hour = "hour";
    // }
    // if (diffDays == 1) {
    //     day = 'day';
    // }
    // if (diffYears == 1) {
    //     year = 'year';
    // }

    // if (diffYears == 0 && diffDays == 0 && diffHours == 0 && diffMins == 0) {
    //     msg = diffSecs + " seconds";
    // }
    // else if (diffYears == 0 && diffDays == 0 && diffHours == 0){
    //     msg = diffMins + " " + min + " and " + diffSecs + " " + second;
    // }
    // else if (diffYears == 0 && diffDays == 0) {
    //     msg = diffHours + " " + hour + ", " + diffMins + " " + min + ", and " + diffSecs + " " + second;
    // }
    // else if (diffYears == 0) {
    //     msg = diffDays + " " + day + ", " + diffHours + " " + hour + ", " + diffMins + " " + min + ", and " + diffSecs + " " + second;
    // }
    // else {
    //     msg = diffYears + " " + year + ", " + diffDays + " " + day + ", " + diffHours + " " + hour + ", " + diffMins + " " + min + ", and " + diffSecs + " " + second;
    // }


    // $("#clock").text(msg);


    const time_obj = format_time();
    let str_tokens = [];
    for (let key in time_obj) {
        if (time_obj[key] === 0) {
            // pass
        } else if (time_obj[key] === 1) {
            str_tokens.push(`${time_obj[key]} ${key.slice(0,-1)}`);
        } else {
            str_tokens.push(`${time_obj[key]} ${key}`);
        }
    }

    let last_elm = str_tokens.pop();
    let format_string = str_tokens.join(', ');
    format_string += ", and " + last_elm;

    // console.log(format_string);
    $("#clock").text(format_string)

//     console.log(diffYears + " years")
//    console.log(diffDays + " days");
//    console.log(diffHours + " hours");
//    console.log(diffMins + " minutes");
//    console.log(diffSecs + " seconds");
};

const monthDay = [31,28,31,30,31,30,31,31,30,31,30,31]

function format_time() {

    const today = new Date();
    const anniversary = new Date(2019, 9, 12);

    let diffYear = today.getFullYear() - anniversary.getUTCFullYear();
    let diffMonth = today.getUTCMonth() - anniversary.getUTCMonth();
    let diffDay = today.getUTCDate() - anniversary.getUTCDate();
    let diffHour = today.getUTCHours() - anniversary.getUTCHours();
    let diffMin = today.getUTCMinutes() - anniversary.getUTCMinutes();
    let diffSecs = today.getUTCSeconds() - anniversary.getUTCSeconds();

    do {
        if (diffMonth < 0) {
            diffYear--;
            diffMonth = 12 + diffMonth;
        }
        if (diffDay < 0) {
            diffMonth--;
    
            if (today.getUTCMonth() === 1 && leap === leapyear(anniversary.getUTCMonth()) === true) {
                diffDay = 29 + diffDay;
            }
            else {
                diffDay = monthDay[today.getUTCMonth()] + diffDay;
            }
        }
        if (diffHour < 0) {
            diffDay--;
            diffHour = 24 + diffHour;
        }
        if (diffMin < 0) {
            diffHour--;
            diffMin = 60 + diffMin;
        }
        if (diffSecs < 0) {
            diffMin--;
            diffSecs = 60 + diffSecs
        }
    } while (diffMonth < 0 && diffDay < 0 && diffHour < 0 && diffMin < 0 && diffSecs < 0)
   

    // console.log(`years: ${diffYear}; months: ${diffMonth}; diffDay: ${diffDay}; hours: ${diffHour}; mins: ${diffMin}; secs: ${diffSecs}`);
    return {'years': diffYear, 'months': diffMonth, 'days': diffDay, 'hours': diffHour, 'minutes': diffMin, 'seconds': diffSecs}

}

function leapyear(year) {
    return (year % 100 === 0) ? (year % 400 === 0) : (year % 4 === 0);
}

function getIPaddress(route) {
    $.ajax({
        url: `/ipaddress/${route}`,
        type: "GET",
        dataType: 'json',
        success: function(res) {
            console.log(res);
            $('#ip').text(res['IP']);
        }});
}

function getStatus(name) {
    $.ajax({
    url: `/status/${name}`,
    type: "GET",
    dataType: 'json',
    success: function(res) {
        console.log(res);
        $('#status').text(res['status']);
    }});
}

function startInstance(name) {
    $.ajax({
    url: `/start/${name}`,
    type: "GET",
    dataType: 'json',
    success: function(res) {
        console.log(res);
        $('#status').text(res['status']);
    }});
}