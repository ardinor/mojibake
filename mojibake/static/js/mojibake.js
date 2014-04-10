jQuery(document).ready(function ($) {
    $("#tabs").tabs();
    $("#post_date").datepicker({ dateFormat: "dd-mm-yy" });
    if (window.location.pathname === "/")
    {
        $('#home_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("posts") !== -1 || window.location.pathname.indexOf("post") !== -1 )
    {
        $('#posts_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("about") !== -1)
    {
        $('#about_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("archive") !== -1)
    {
        $('#archive_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("tags") !== -1)
    {
        $('#tags_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("categories") !== -1)
    {
        $('#categories_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("contact") !== -1)
    {
        $('#contact_tab').addClass('active');
    }

});
