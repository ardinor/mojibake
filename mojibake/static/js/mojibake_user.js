$(function() {
    //$("#post_body").wysihtml5();
    $('#tags').tagsInput();
    //$("#tags_list").tags({
    //
    //    })
    //$('#post_body').val(); to get the html
    //$(".btn-success").click(function() {
    $("#approve").click(function() {
        var parent = $(this).parents("#comment-row");
        var gparent = parent.parent();
        //var comm_text = parent.find("#comment").text();
        //var author = parent.find("#comment").attr("author");
        //var body = parent.find("#comment").attr("body");
        var ref = parent.find("#comment").attr("ref");
        var jqxhr = $.getJSON($SCRIPT_ROOT + '/panel/comment/approve', {
            ref: ref
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
        window.setTimeout(function() {hideChildren(gparent);}, 300);
        });
    });
    $("#delete").click(function() {
        var parent = $(this).parents("#comment-row");
        var gparent = parent.parent();
        //var comm_text = parent.find("#comment").text();
        //var author = parent.find("#comment").attr("author");
        //var body = parent.find("#comment").attr("body");
        var ref = parent.find("#comment").attr("ref");
        var jqxhr = $.getJSON($SCRIPT_ROOT + '/panel/comment/delete', {
            ref: ref
        },
        function(data) {
            $.pnotify({
                text: 'Comment deleted',
                delay: 700,
                type: 'success',
                animation: 'show',
                history: false
            });
        parent.hide("fast");
        window.setTimeout(function() {hideChildren(gparent);}, 300);
        });
    });
});