function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

$(function () {
    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });
});

$(function () {
    $(document).on('click', '.thanks', function () {
        taskid = this.parentElement.getAttribute('taskid');
        $.ajax({
            type: "POST",
            url: "/thanks/",
            data: "taskid=" + taskid,
            cache: false,
            success: function (data) {
                htmldata = '<p>Рейтинг задачи: ' + data['rating'] + '</p>';
                $('[taskid=' + taskid + ']').html(htmldata)
            }
        })
    });
});

$(function () {
    $(document).on('click', '.dislike', function () {
        dislike(this);
    })
});

function likeFunction(caller) {
    var postId = caller.parentElement.getAttribute('postid');
    $.ajax({
        type: "POST",
        url: "/rate/",
        data: "Action=LIKE&PostId=" + postId,
        cache: false,
        success: function (data) {
            htmldata = '<button class="btn btn-default like disabled" id="' + postId + 'like">' +
                ' <i class="fa fa-thumbs-up" aria-hidden="true"></i>' +
                '</button>' +
                '<span> ' + data['count'] + ' </span>' +
                '<button class="btn btn-default dislike" id="' + postId + 'dislike">' +
                ' <i class="fa fa-thumbs-o-down" aria-hidden="true"></i>' +
                '</button>';
            $('#postid' + postId).html(htmldata)
        }
    })
}

function dislike(caller) {
    var postId = caller.parentElement.getAttribute('postid');
    $.ajax({
        type: "POST",
        url: "/rate/",
        data: "Action=DISLIKE&PostId=" + postId,
        cache: false,
        success: function (data) {
            htmldata = '<button class="btn btn-default like" id="' + postId + 'like">' +
                ' <i class="fa fa-thumbs-o-up" aria-hidden="true"></i>' +
                '</button>' +
                '<span> ' + data['count'] + ' </span>' +
                '<button class="btn btn-default disabled dislike" id="' + postId + 'dislike">' +
                ' <i class="fa fa-thumbs-down" aria-hidden="true"></i>' +
                '</button>';
            $('#postid' + postId).html(htmldata)
        }
    })
}

$(function () {
    $('.answer_checkbox').click(function () {
        var answerid = this.parentElement.getAttribute('answerid');
        var postid = this.parentElement.getAttribute('postid');
        var checked = this.getAttribute('checked');
        $.ajax({
            type: 'POST',
            url: '/rate/',
            data: 'answerid=' + answerid + '&postid=' + postid + '&checked=' + checked,
            cache: false,
            success: function () {
                if (checked == 'checked') {
                    $('#' + answerid).removeAttr('checked');
                }
                else {
                    $('.answer_checkbox').removeAttr('checked');
                    $('#' + answerid).prop('checked', 'checked');
                }
            }
        })
    })
});