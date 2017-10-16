
function loadLazyContainer(query_str) {

    query_str = query_str + "&page=" + $("#statements-page").val();

    $.ajax(url_lazy_content, {
        data: query_str
    })
    .done(function (data) {
        $("#lazy-container").html(data);
    });
}