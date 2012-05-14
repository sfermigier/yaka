<!-- live search -->
$(document).ready(function() {
  $("#search-box").keyup(function() {
    var q = $(this).val();
    if (q == '') {
      $("#live-search-results").html("").hide();
    } else {
      $.ajax({
        type: "GET",
        url: "/search/live?q=" + q,
        cache: false,
        success: function(html) {
          if (html) {
            $("#live-search-results").html(html).show();
          } else {
            $("#live-search-results").html("").hide();
          }
        }
      });
    }
    return false;
  });
});
