// Code retrieved from:
// https://www.w3schools.com/howto/howto_js_countdown.asp 

$(document).ready(function () {

    // Set the date we're counting down to
    var startAt = document.getElementById("cuenta-atras").value;
    var now = 0;
    //Update the count down every 1 second


    var x = setInterval(function () {


        //check if all participants have answered
        $.ajax({
            url: "/services/checkAllAnswered/",
            success: function (data) {
                // fill the content of the div with the data returned by the server
                console.log(data);
                if (data == "True") {
                    window.location.href = "/services/gamecountdown";
                }
            }
        });
        
        
        // Get today's date and time
        now = now + 1;

        // Find the distance between now and the count down date
        var distance = startAt - now;

        // Output the result 
        document.getElementById("countdown").innerHTML = distance;

        // If the count down is over, write some text 
        if (distance == 0) {
            clearInterval(x);
            window.location.href = "/services/gamecountdown";
        }
    }, 1000);
});