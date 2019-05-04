$(function () {
    $("#guidebook").click(function () {
        var a = $(this).attr("data-link");
        window.open(a)
    });
    if (is_ie() == false) {
        Webcam.set({
            width: 336,
            height: 240,
            image_format: 'jpg',
            jpeg_quality: 90
        });
        Webcam.on('load', function () {
            $("#concel").show();
            $("#activeAuthentication").hide();
            $(".content_login_box").css("height", "567px");
            if ($("#apps_bar").is(":hidden")) {
                $(".link_box_right").hide()
            }
        });
        Webcam.on('live', function () {
            $("#confirm").show()
        });
        Webcam.on('error', function (a) {
            $("#concel").click()
        });
        initCamera()
    } else {
        $("#activeAuthentication").hide();
        if (is_ie() == 'ie7') {
            $("input[name='code']").css({
                "margin-left": "-12px"
            })
        }
    }
    var f = location.search;
    if (f.indexOf("service.ecnu.edu.cn") != -1 || f.indexOf("oaindex.jsp") != -1 || f.indexOf("treasury.ecnu.edu.cn") != -1 || f.indexOf("applicationidc.ecnu.edu.cn") != -1 || f.indexOf("applicationnewjw.ecnu.edu.cn") != -1) {
        $("#apps_bar").hide();
        $("body").css("background-image", "url(comm/image/container_02.jpg)")
    } else {
        $("#apps_bar").show();
        $("body").css("background-image", "url(comm/image/container_01.jpg)")
    }
    var g = document.getElementById("account_template").innerHTML;
    $("#accountlogin").unbind("click").bind("click", function () {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active").siblings().removeClass("active");
            $.getScript("comm/js/placeholderfriend.js");
            $(".login_box_title").css("margin-bottom", "");
            $("#logincontainer").html(g);
            if (is_ie() == false) {
                initCamera()
            } else {
                $("#activeAuthentication").hide();
                if (is_ie() == 'ie7' && is_ie() != 'ie8') {
                    $("input[name='code']").css({
                        "margin-left": "-12px"
                    })
                }
            }
            $("#index_login_btn").unbind("click").bind("click", function () {
                login()
            });
            $("#un").keyup(function (e) {
                if (e.which == 13) {
                    login()
                }
            }).keydown(function (e) {
                $(this).parent().removeClass("login_error_border");
                $("#errormsg").parent().hide()
            });
            $("#pd").keyup(function (e) {
                if (e.which == 13) {
                    login()
                }
            }).keydown(function (e) {
                $(this).parent().removeClass("login_error_border");
                $("#errormsg").parent().hide()
            });
            $("#code").unbind().keyup(function (e) {
                if (e.which == 13) {
                    login()
                }
            })
        }
    });
    $("#accountlogin").trigger("click");
    var h = new loginQRCode("qrcode", 153, 153);
    var i = document.getElementById("weixin_template").innerHTML;
    $("#weixinlogin").unbind("click").bind("click", function () {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active").siblings().removeClass("active");
            $(".login_box_title").css("margin-bottom", "50px");
            $("#errormsg").parent().hide();
            $("#logincontainer").html(i);
            if (is_ie() == 'ie8') {
                $("#qrcode").addClass("qr_code_ie8");
                $(".login_code_notice").addClass("qr_notice_ie8")
            } else {
                $("#qrcode").addClass("qr_code_normal");
                $(".login_code_notice").addClass("qr_notice_normal")
            }
            h.generateLoginQRCode(function (a) {
                var b = GetQueryString("service");
                if (a) {
                    window.location.href = "https://portal1.ecnu.edu.cn/tp_tpass/h5?act=tpass/guide"
                } else {
                    if (b != null) {
                        window.location.href = b
                    } else {
                        window.location.href = default_redirect_url
                    }
                }
            })
        }
    });
    if ($("#errormsg").text()) {
        $("#errormsg").parent().show()
    }
    var j = {
        imageWidth: 1680,
        imageHeight: 1050
    };
    var k = function () {
        var a = $(window).height();
        var b = $(window).width();
        $(".login_conatiner").css("height", a);
        $(".login_conatiner").css("width", b);
        $("#container_bg").css("height", a);
        $("#container_bg").css("width", b);
        $("#login_right_box").css("height", a);
        var c = j.imageWidth;
        var d = j.imageHeight;
        var e = d / c;
        c = b;
        d = Math.round(b * e);
        if (d < a) {
            d = a;
            c = Math.round(d / e)
        }
        $(".login_img_01").width(c).height(d)
    };
    k();
    $(window).resize(function () {
        k()
    })
});
var facedata = "";

function login() {
    var a = $("#un"),
        $p = $("#pd");
    var u = a.val().trim();
    if (u == "") {
        a.focus();
        a.parent().addClass("login_error_border");
        return
    }
    var p = $p.val().trim();
    if (p == "") {
        $p.focus();
        $p.parent().addClass("login_error_border");
        return
    }
    a.attr("disabled", "disabled");
    $p.attr("disabled", "disabled");
    var b = $("#lt").val();
    $("#ul").val(u.length);
    $("#pl").val(p.length);
    $("#rsa").val(strEnc(u + p + b, '1', '2', '3'));
    $("input[name='loginFace']").attr("value", facedata);
    $("#loginForm")[0].submit()
};

function refreshCodeImg() {
    $("#codeImage").attr("src", "code?" + Math.random())
};
String.prototype.trim = function () {
    return this.replace(/^\s\s*/, '').replace(/\s\s*$/, '')
};
var is_ie = function () {
    if (navigator.appName == "Microsoft Internet Explorer" && navigator.appVersion.split(";")[1].replace(/[ ]/g, "") == "MSIE7.0") {
        return 'ie7'
    } else if (navigator.appName == "Microsoft Internet Explorer" && navigator.appVersion.split(";")[1].replace(/[ ]/g, "") == "MSIE8.0") {
        return 'ie8'
    } else {
        return false
    }
};

function initCamera() {
    $("#activeAuthentication").unbind().bind('click', function () {
        Webcam.reset();
        Webcam.attach('#my_camera')
    });
    $("#concel").unbind("click").bind("click", function () {
        Webcam.reset();
        $(this).hide();
        $("#activeAuthentication").show();
        $("#again").hide();
        $("#confirm").hide();
        $("#my_camera").removeAttr("style");
        $("#my_face").attr("src", "").hide();
        facedata = "";
        $("input[name='loginFace']").attr("value", "");
        $(".content_login_box").css("height", "373px");
        if ($("#apps_bar").is(":hidden")) {
            $(".link_box_right").show()
        }
    });
    $("#confirm").click(function () {
        Webcam.snap(function (a) {
            $("#my_face").attr("src", a).show();
            facedata = a;
            $("input[name='loginFace']").attr("value", a)
        });
        Webcam.reset();
        $(this).hide();
        $("#again").show();
        $("#my_camera").removeAttr("style")
    });
    $("#again").click(function () {
        $(this).hide();
        $("#confirm").show();
        $("#my_face").attr("src", "").hide();
        Webcam.attach('#my_camera');
        facedata = "";
        $("input[name='loginFace']").attr("value", "")
    })
};

function GetQueryString(a) {
    var b = new RegExp("(^|&)" + a + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(b);
    if (r != null) return unescape(r[2]);
    return null
};