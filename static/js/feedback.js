function disableButton() {
    $("#button-submit").attr("disabled", "disabled");
    $("#text-button-submit").text("正在提交...")
}

function enableButton() {
    $("#button-submit").removeAttr("disabled");
    $("#text-button-submit").text("提交")
}


function subMitFeedback() {
    if ($("#input-message").val() == '') {
        $("#input-message").focus();
        return;
    }
    $("#div-error").fadeOut(300);
    $("#div-spinner").fadeIn(500);
    disableButton();
    data = new FormData();
    data.append("message", $("#input-message").val())
    data.append("contact", $("#input-contact").val())
    data.append('file', $('#input-file').prop("files")[0]);

    $.ajax({
        type: "POST",
        enctype: 'multipart/form-data',
        url: "/sendFeedback",//url
        processData: false,
        contentType: false,
        cache: false,
        data: data,
        success: function (result) {
            //todo 数据验证
            console.log(result);//打印服务端返回的数据(调试用)
            if (result.success == true) {
                $("#div-error").fadeOut(300);
                $("#div-spinner").fadeOut(500);
                mdui.snackbar("发送成功")
            } else {
                $("#div-error").fadeIn(300);
                $("#text-error").text("Telegram 服务器暂时不可用，请再试一次。")
                $("#div-spinner").fadeOut(500);
            }
            enableButton();

        },
        error: function (result) {
            console.error(result)
            $("#div-error").fadeIn(300);
            $("#text-error").text("出现未知错误，请再试一次。")
            $("#div-spinner").fadeOut(500);
            enableButton();
        }
    })

}

window.onload = function () {

    $("#div-spinner").hide();
    $("#div-error").hide();
    $(document).keyup(function (event) {
        if (event.keyCode == 13 && $("#input-contact").is(":focus")) {
            subMitFeedback();
        }

    });

}