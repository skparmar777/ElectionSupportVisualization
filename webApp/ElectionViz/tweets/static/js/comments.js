// global variable COMMENTS, USER, and PASSWORD is assumed to be set by HTML
// should be an array of {name, date, comment}
var DATETIME_OFFSET = new Date().getTimezoneOffset(); // converts database UTC time to localtime
let USERNAME = null;
let PASSWORD = null;

function handle_comments_click() {
    if ($(".open-button").text() === "Undo") {
        var xhttp = new XMLHttpRequest();
        const params = `name=${USERNAME}&password=${PASSWORD}&undo=true`;
        xhttp.onreadystatechange = function() {
            if (xhttp.readyState === 4 && xhttp.status === 200) {
                // render the comments (should contain the new comments)
                get_recent_comments();
                render_comments();
            }
            else if (xhttp.readyState === 4 && xhttp.status === 400) {
                console.log("unsure how this happened - invalid params?");
            }
        };
        xhttp.open("POST", "/comments/", false);
        xhttp.send(params);
        $(".open-button").text("Leave a Comment");
        return;
    }
    document.getElementById("myForm").style.display = "block";
}
  
function close_comments() {
    document.getElementById("myForm").style.display = "none";
}

$("#send-comments").click(function() {
    USERNAME = $("#username").val();
    PASSWORD = $("#password").val();
    const comments = $("#comments").val();
    console.log(username, password);
    var xhttp = new XMLHttpRequest();
    const params = `name=${USERNAME}&password=${PASSWORD}&comment=${comments}`;
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState === 4 && xhttp.status === 200) {
            
            // render the comments (should contain the new comments)
            get_recent_comments();
            render_comments();
            close_comments();
            $(".open-button").text("Undo");
        }
        else if (xhttp.readyState === 4 && xhttp.status === 400) {
            console.log("invalid params");
        }
    };
    xhttp.open("POST", "/comments/", false);
    xhttp.send(params);
});

const add_comments = function(name, date, comment) {
    const date_string = formatAMPM(date) + " "
    const new_div = `<span class='date'>${date_string}</span> \
                    <span class='name'>${name + ": "}</span> \
                    <span class='comment'>${comment}</span> \
                    </div>`
    $("<div class='data-comment'>").html(new_div).appendTo('#comments-list');
};

function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

const render_comments = () => {
    // clear existing list, redraw
    const parent = document.getElementById("comments-list");
    while (parent.firstChild) {
        parent.firstChild.remove();
    }
    for (let i = 0; i < COMMENTS.length; i++) {
        const ct = new Date(COMMENTS[i].date);
        ct.setMinutes(ct.getMinutes() - DATETIME_OFFSET);
        add_comments(COMMENTS[i].name, ct, COMMENTS[i].comment);
    }
}

const get_recent_comments = () => {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState === 4 && xhttp.status === 200) {
            // render the new data
            COMMENTS = JSON.parse(xhttp.responseText);
        }
    };
    xhttp.open("GET", "/comments/", false);
    xhttp.send();
}

render_comments();

