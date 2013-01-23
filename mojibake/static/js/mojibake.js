$(function() {
    $("#divLogin").css("display", "block");
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
    function hideChildren(gparent) {
           if(gparent.children("div:visible").length == 1) {
                gparent.hide("fast");
            };
    };
    $(".btn-success").click(function() {
        var parent = $(this).parents("#comment-row");
        var gparent = parent.parent();
        var comm_text = parent.find("#comment").text();
        var jqxhr = $.getJSON($SCRIPT_ROOT + '/panel/comment/approve', {
            comment: comm_text
        },
        function(data) {
            $.pnotify({
                text: 'Comment approved',
                delay: 700,
                type: 'success',
                animation: 'show',
                history: false
            });
        parent.hide("fast");
        window.setTimeout(function() {hideChildren(gparent)}, 300);
        });
    });
});