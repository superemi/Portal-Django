$(function(){
    $('.progress-card .panel').mouseover(function(){
        $(this).find('.progress').addClass('active progress-striped');
    });
    $('.progress-card .panel').mouseout(function(){
        $(this).find('.progress').removeClass('active progress-striped');
    });
    $('.collapse').on('hide.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right')
    })
    $('.collapse').on('show.bs.collapse', function () {
        $(this).parent().find('.page-header').find('span.glyphicon').removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down')
    })
});
function toggleFollowProgresses(btn){
    $(btn).toggleClass("active").children().toggleClass("text-warning")
    $(btn).find(".glyphicon").toggleClass("glyphicon-unchecked").toggleClass("glyphicon-check")
    $("#follow-row").toggleClass("hidden")
    $("#inprogress-and-follow-row").toggleClass("hidden")
}
function toggleSearchRow(btn){
    if (typeof prev_scrollTop == "undefined"){
        var target_scrollTop = 0
        prev_scrollTop = document.documentElement.scrollTop
    } else {
        var target_scrollTop = document.documentElement.scrollTop || prev_scrollTop
        delete prev_scrollTop
    }
    $("html, body").animate({ scrollTop: target_scrollTop }, 200)
    $("#search-row").slideToggle('fast')
    $("#search-input").focus()
    $(btn).toggleClass("active")
}
