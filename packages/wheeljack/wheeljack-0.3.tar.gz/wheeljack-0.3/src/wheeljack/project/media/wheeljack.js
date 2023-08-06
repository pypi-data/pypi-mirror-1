function updateBuildLog() {
    // jQuery.getJSON("/api/project/2/log/latest")
    jQuery("link").each(function(i, link) {
        if(link.rel == "buildlog") {
            jQuery.getJSON(link.href, null, function (data) {
                jQuery("#output").text(data["output"]);
                var state = jQuery("#build-state");
                state.text(data["state"]);
                state.attr("class", data["state"].toLowerCase());
                jQuery("#build-time").text(data["buildtime"]);
            });
        }
    });
}

setInterval(updateBuildLog, 1000);