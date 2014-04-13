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
    $("#post_body").keydown(function(e) {
      var $this, end, start;
      if (e.keyCode === 9) {
        start = this.selectionStart;
        end = this.selectionEnd;
        $this = $(this);
        $this.val($this.val().substring(0, start) + "\t" + $this.val().substring(end));
        this.selectionStart = this.selectionEnd = start + 1;
        return false;
      }
    });
    $("#post_body_ja").keydown(function(e) {
      var $this, end, start;
      if (e.keyCode === 9) {
        start = this.selectionStart;
        end = this.selectionEnd;
        $this = $(this);
        $this.val($this.val().substring(0, start) + "\t" + $this.val().substring(end));
        this.selectionStart = this.selectionEnd = start + 1;
        return false;
      }
    });

});
