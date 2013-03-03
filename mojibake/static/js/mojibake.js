$(function() {
    $("#divLogin").css("display", "block");
    //$("#tags_list").tags({
    //
    //    })
    //$('#post_body').val(); to get the html
    $('[data-toggle="modal"]').click(function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        if (url.indexOf('#') == 0) {
            $(url).modal('open');
        } else {
            $.get(url, function(data) {
                $('<div class="modal hide fade">' + data + '</div>').modal();
            }).success(function() { $('input:text:visible:first').focus(); });
        }
    });
});