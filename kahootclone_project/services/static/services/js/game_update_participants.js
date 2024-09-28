// script to make an asynchronous call to the server to update the 
// participants list.

$(document).ready(function () {
  function refresh() {
    $.ajax({
      url: "/services/gameUpdateParticipant/",
      success: function (data) {
        // fill the content of the div with the data returned by the server
        $('#participants_list').html(data);
      }
    });
    // call the function again after 2 seconds
    setTimeout(refresh, 2000);
  }

  $(function () {
    refresh();
  });

});