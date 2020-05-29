var currentStep = 0
var divMainWidth = 0
var downloadLink = ""

function switchStep(newStep, quick=false) {
    divMainWidth = $("#div-main").width()
    var easeTime = 1000
    if(quick == true){
        easeTime = 300
    }
    $("#div-slider").animate({left: (-divMainWidth * newStep) + "px"}, {duration: easeTime, queue: false, easing: "easeInOutExpo"});
    $("#div-slider").animate({height: $("#step" + newStep).height()}, {duration: easeTime, queue: false, easing: "easeInOutExpo"})

    $("#progressbar").css('width', 30 * newStep + '%');
    currentStep = newStep
}


function userLogin() {
    $("#div-error").fadeOut(300);
    $("#div-spinner").fadeIn(500);
    if($("#input-username").val() == '' ||  $("#input-password").val() == ''){
        return
    }
    $.ajax({
        //几个参数需要注意一下
        type: "GET",//方法类型
        dataType: "json",//预期服务器返回的数据类型
        url: "/logIn",//url
        timeout: 60000,
        data: $('#formLogin').serialize(),
        success: function (result) {
            console.log(result);//打印服务端返回的数据(调试用)
            if (result.success == true) {
                $("#div-error").fadeOut(300);
                $("#text-realname").text("已登录为" + result.data.realname)
                switchStep(currentStep + 1)
                $("#div-spinner").fadeOut(500);
            } else {
                $("#div-error").fadeIn(300);
                $("#text-error").text(result.message)
                $("#div-spinner").fadeOut(500);
                switchStep(currentStep)
            }
        },
        error: function (error) {
            console.error(error);
            $("#div-error").fadeIn(300);
            $("#text-error").text("暂时无法连接至数据库。\n学校的土豆🥔服务器又双叒叕炸了。")
            switchStep(currentStep)
            $("#div-spinner").fadeOut(500);
        }
    });

}

function getCSV() {
    $("#div-error-step2").fadeOut(300);
    $("#div-spinner").fadeIn(500);
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/getClass",
        data: {
            "semester": $("#select-semester").val()
        },
        success: function (result1) {
            console.log(result1);

            $.ajax({
                type: "GET",
                dataType: "json",
                url: "/getCSV",
                data: $("#formGetCSV").serialize(),
                success: function (result) {
                    console.log(result);
                    $("#div-nav-next").hide();
                    $("#div-nav-download").show();
                    $("#div-spinner").fadeOut(500);
                    downloadLink = result.data.link
                    printTable(result1)
                    $("#div-feedback").fadeIn(1000);
                    switchStep(currentStep + 1);

                },
                error: function (error) {
                    console.error(error);
                    $("#div-error-step2").fadeIn(300);
                    $("#text-error-step2").text("出现错误，可能是会话已过期，请刷新网页。")
                    switchStep(currentStep)
                    $("#div-spinner").fadeOut(500);
                }
            })

        },
        error: function (error) {
            console.error(error);
            $("#div-error-step2").fadeIn(300);
            $("#text-error-step2").text("无法解析课程表。可能是会话已过期，请刷新网页。也可能是你的课程表比较特别，暂时无法处理。希望你能帮忙在侧边栏选择反馈提交一下。")
            switchStep(currentStep)
            $("#div-spinner").fadeOut(500);
        }
    })
}

function printTable(result) {
    var html = "";
    var classNames = []
    result.data.classes.forEach(function (oneClass) {
        if(classNames.indexOf(oneClass.name) == -1){
            html += "<tr>";
            html += "<td>" + oneClass.name + "</td>";
            html += "<td>" + oneClass.teacher + "</td>";
            html += "<td>" + oneClass.classroom + "</td>";
            html += "</tr>";
            classNames.push(oneClass.name)
        }

    })
    $("#tbody-result").html(html);
}

function nextStep() {
    switch (currentStep) {
        case 0:
            $("#button-last").removeAttr("disabled");
            $("#div-nav-last").fadeIn(300);
            switchStep(currentStep + 1)
            break;
        case 1:
            userLogin();
            break;
        case 2:
            getCSV();

            break;
    }

}

function lastStep() {
    switch (currentStep) {
        case 1:
            $("#div-nav-last").fadeOut(300);
            $("#button-last").attr("disabled", "disabled");
            break;
        case 3:
            $("#div-nav-next").show();
            $("#div-nav-download").hide();
            $("#div-feedback").fadeOut(500);
            break;
    }
    switchStep(currentStep - 1)
}

function downloadCSV() {
    $("#progressbar").css('width', '100%');
    var $form = $('<form method="GET"></form>');
    $form.attr('action', downloadLink);
    $form.appendTo($('body'));
    $form.submit();
}

window.onload = function () {
    divMainWidth = $("#div-main").width()
    $("#div-nav-download").hide();
    $("#div-nav-last").hide();
    $("#div-error").hide();
    $("#div-error-step2").hide();

    $("#div-spinner").hide();

    $(document).keyup(function (event) {
        if($("#div-spinner").css('display') != 'none'){
            return;
        }
        if (event.keyCode == 13) {
            if (currentStep != 3) {
                nextStep();
            }
        } else if (event.keyCode == 27) {
            if (currentStep != 0) {
                lastStep();
            }
        }
    });


}

$(document).ready(function () {
    var rtime;
    var timeout = false;
    var delta = 100;
    $(window).resize(function () {
        rtime = new Date();
        if (timeout === false) {
            timeout = true;
            setTimeout(resizeend, delta);
        }
    });

    function resizeend() {
        if (new Date() - rtime < delta) {
            setTimeout(resizeend, delta);
        } else {
            timeout = false;
            switchStep(currentStep, true);
            console.log("Window resized.");
        }
    }

})


