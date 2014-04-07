$(function() {
    if (window.location.pathname === "/")
    {
        $('#home_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("posts") !== -1)
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
        if (window.location.pathname === '/categories/')
        {
            $('#categories_tab').addClass('active');
        }
        else
        {
            var tabName = window.location.pathname.replace('/categories/', '');
            tabName = '#' + tabName.replace('/', '') + '_tab';
            $(tabName).addClass('active');
        }
    }
    if (window.location.pathname.indexOf("contact") !== -1)
    {
        $('#contact_tab').addClass('active');
    }
});
