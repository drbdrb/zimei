// 睫毛
var eyelash = function(ctx, mox, moy, cpx, cpy, x, y, fstyle) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.quadraticCurveTo(cpx, cpy, x, y);
    ctx.closePath();
    ctx.fillStyle = fstyle;
    ctx.fill();
}

//睁眼
// 眼眶
var eyelid = function(ctx, cx, cy, rc, ry, angle, sAngle, eAngle, fstyle) {
    ctx.beginPath();
    ctx.ellipse(cx, cy, rc, ry, angle, sAngle, eAngle);
    ctx.fillStyle = fstyle;
    ctx.fill();
}

//绘制眼球
var eyeball = function(ctx, cx, cy, cr, sAngle, eAngle, fstyle) {
    ctx.beginPath();
    ctx.arc(cx, cy, cr, sAngle, eAngle);
    ctx.fillStyle = fstyle;
    ctx.fill();
}

// 眨眼
var wink = function(ctx, lines, mox, moy, linex1, liney1, linex2, liney2, width, fstyle) {
    ctx.beginPath();
    ctx.lineJoin = lines;
    ctx.moveTo(mox, moy);
    ctx.lineTo(linex1, liney1);
    ctx.lineTo(linex2, liney2);
    ctx.lineWidth = width;
    ctx.fillStyle = fstyle;
    ctx.stroke();
}

// 微笑
var smile = function(ctx, mox, moy, cp1x, cp1y, cp2x, cp2y, x, y, fstyle, sstyle, width, lines) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);
    ctx.fillStyle = fstyle;
    ctx.strokeStyle = sstyle;
    ctx.lineWidth = width;
    ctx.lineJoin = lines;
    ctx.fill();
    ctx.closePath();
    ctx.stroke();
}

// 张嘴
// 填充
var openmouth = function(ctx, mox, moy, linex1, liney1, linex2, liney2, linex3, liney3, fstyle) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.lineTo(linex1, liney1);
    ctx.lineTo(linex2, liney2);
    ctx.lineTo(linex3, liney3);
    ctx.closePath();
    ctx.fillStyle = fstyle;
    ctx.fill();
}

// 左右
var mouthLeft = function(ctx, mox, moy, cp1x, cp1y, cp2x, cp2y, x, y, fstyle, sstyle, width) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);
    ctx.fillStyle = fstyle;
    ctx.fill();
    ctx.strokeStyle = sstyle;
    ctx.lineWidth = width;
    ctx.stroke();
}

// 上下
var mouthTop = function(ctx, mox, moy, cpx, cpy, x, y, sstyle, width) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.quadraticCurveTo(cpx, cpy, x, y);
    ctx.strokeStyle = sstyle;
    ctx.lineWidth = width;
    ctx.stroke();
}

// 下
var mouthBottom = function(ctx, mox, moy, cpx, cpy, x, y, sstyle, width, fstyle) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.quadraticCurveTo(cpx, cpy, x, y);
    ctx.strokeStyle = sstyle;
    ctx.lineWidth = width;
    ctx.fillStyle = fstyle;
    ctx.fill();
    ctx.stroke();
}

// 舌头
var tongue = function(ctx, mox, moy, cpx, cpy, x, y, sstyle) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.quadraticCurveTo(cpx, cpy, x, y);
    ctx.fillStyle = sstyle;
    ctx.fill();
}

// 惊讶
var shock = function(ctx, cx, cy, rc, ry, angle, sAngle, eAngle, width, sstyle) {
    ctx.beginPath();
    ctx.ellipse(cx, cy, rc, ry, angle, sAngle, eAngle);
    ctx.lineWidth = width;
    ctx.strokeStyle = sstyle;
    ctx.stroke();
}

// 侧脸  耳朵
var ear = function(ctx, mox, moy, cp1x, cp1y, cp2x, cp2y, x, y, width) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y);
    ctx.lineWidth = width;
    ctx.stroke();

}
var ear1 = function(ctx, mox, moy, cpx, cpy, x, y, width) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.quadraticCurveTo(cpx, cpy, x, y);
    ctx.lineWidth = width;
    ctx.stroke();
}

// 声波
var draw = function(ctx, mox, moy, cpx, cpy, x, y, a, b, c, d, e, f, scalewidth, scaleheight, number, width) {
    ctx.beginPath();
    ctx.moveTo(mox, moy);
    ctx.quadraticCurveTo(cpx, cpy, x, y);
    ctx.transform(a, b, c, d, e, f);
    ctx.scale(scalewidth, scaleheight);
    ctx.globalAlpha = ctx.globalAlpha - number;
    ctx.lineWidth = width;
    ctx.stroke();
}

// 耳朵
var halfEar = function() {
    var ctx4 = myCanvas4.getContext('2d');

    ear(ctx4, 20, 80, 100, 45, 130, 185, 20, 220, 5);
    ear1(ctx4, 40, 105, 70, 115, 57, 155, 5);
    ear1(ctx4, 43, 135, 28, 160, 48, 185, 5);
}

// 声波
var soundWave = function(i) {
    var ctx4 = myCanvas5.getContext('2d');

    switch (i) {
        case 0:
            break;
        case 1:
            draw(ctx4, 40, 125, 70, 135, 57, 175, 1, 0, 0, 1, 10, -35, 1.2, 1.2, 0.2, 3)
            break;
    }
}

// 声波的速度
setInterval(function() {
    var ctx4 = myCanvas5.getContext("2d");
    if (ctx4.globalAlpha > 0.1) { //当透明值大于0.1时，声波显示
        soundWave(1);
    } else {
        // clear();
        myCanvas5.height = myCanvas5.height; //改变画布的高度，清除画布
        ctx4.globalAlpha = 1; //透明度变为1
    }
}, 80)

// 侧脸
var sideFace = function() {
    var ctx3 = myCanvas3.getContext('2d');

    // 左眼
    eyelid(ctx3, 70, 90, 23, 43, 0, 0, Math.PI * 2, "#111")

    //绘制左眼球
    eyelid(ctx3, 65, 75, 7, 10, 0.3, 0, Math.PI * 2, "#ddd")

    eyelid(ctx3, 75, 115, 4, 6, 0.4, 0, Math.PI * 2, "#ddd")


    // 右眼
    eyelid(ctx3, 185, 90, 40, 60, 0, 0, Math.PI * 2, "#111")

    //绘制右眼球
    eyelid(ctx3, 175, 65, 15, 22, 0.4, 0, Math.PI * 2, "#ddd")

    eyelid(ctx3, 195, 125, 7, 10, 0.4, 0, Math.PI * 2, "#ddd")

    // 绘制右眼神光
    eyeball(ctx3, 175, 60, 4, 0, 2 * Math.PI, "#fff")

    eyeball(ctx3, 175, 75, 3, 0, 2 * Math.PI, "#fff")

    // 嘴巴
    tongue(ctx3, 83, 250, 97, 271, 130, 240, "red"); // 舌头
    mouthTop(ctx3, 70, 225, 70, 245, 140, 226, "#990000", 5) // 上
    mouthTop(ctx3, 80, 235, 85, 290, 140, 226, "#990000", 5) // 下
}


// 左眼
var leftEye = function(i) {
    var ctx = myCanvas.getContext('2d');

    ctx.clearRect(0, 0, 200, 170); //清画布
    switch (i) {
        case 0: //闭眼
            // 左睫毛一
            eyelash(ctx, 45, 86, 28, 82, 26, 92, "#111");

            eyelash(ctx, 48, 88, 28, 84, 24, 93, "white");

            // 左睫毛二
            eyelash(ctx, 50, 85, 55, 101, 37, 100, "#111");

            eyelash(ctx, 50, 83, 55, 97, 37, 99, "white");

            // 左睫毛三
            eyelash(ctx, 83, 93, 70, 115, 53, 113, "#111");

            eyelash(ctx, 80, 90, 70, 110, 53, 112, "white");

            // 左睫毛四
            eyelash(ctx, 100, 105, 85, 127, 72, 125, "#111");

            eyelash(ctx, 97, 102, 85, 122, 72, 124, "white");

            // 左睫毛五
            eyelash(ctx, 117, 111, 108, 135, 98, 132, "#111");

            eyelash(ctx, 114, 108, 108, 130, 98, 132, "white");

            // 左睫毛六
            eyelash(ctx, 123, 105, 136, 127, 148, 128, "#111");

            eyelash(ctx, 126, 102, 138, 122, 146, 127, "white");

            // 左睫毛七
            eyelash(ctx, 140, 95, 155, 117, 172, 117, "#111");

            eyelash(ctx, 143, 92, 155, 112, 172, 116, "white");

            // 左睫毛八
            eyelash(ctx, 170, 89, 168, 101, 186, 100, "#111");

            eyelash(ctx, 170, 87, 168, 97, 186, 99, "white");

            // 左下弯眼
            eyelash(ctx, 185, 85, 115, 145, 35, 85, "#111");

            eyelash(ctx, 185, 80, 115, 135, 38, 85, "white");

            break;

        case 1: //睁眼
            // 左眼
            eyelid(ctx, 100, 85, 70, 80, 0, 0, Math.PI * 2, "#111")

            //绘制左眼球
            eyeball(ctx, 80, 55, 25, 0, 2 * Math.PI, "#ddd")

            eyeball(ctx, 120, 135, 10, 0, 2 * Math.PI, "#ddd")

            //绘制左眼神光
            eyeball(ctx, 95, 50, 5, 0, 2 * Math.PI, "#fff")

            eyeball(ctx, 87, 40, 3, 0, 2 * Math.PI, "#fff")

            break;

        case 2:
            // 左眼
            // 眨眼
            wink(ctx, "round", 50, 30, 150, 80, 50, 130, 9, "#000")

            break;

    }

}

// 右眼
var rightEye = function(i) {
    var ctx1 = myCanvas1.getContext('2d');
    ctx1.clearRect(0, 0, 200, 170); //清画布

    switch (i) {
        case 0: //闭眼
            // 右睫毛一
            eyelash(ctx1, 155, 86, 172, 82, 174, 92, "#111")

            eyelash(ctx1, 152, 88, 172, 84, 176, 93, "white")

            // 右睫毛二
            eyelash(ctx1, 150, 85, 145, 101, 163, 100, "#111")

            eyelash(ctx1, 150, 83, 145, 97, 163, 99, "white")

            // 右睫毛三
            eyelash(ctx1, 117, 93, 130, 115, 147, 113, "#111")

            eyelash(ctx1, 114, 90, 130, 110, 147, 112, "white")

            // 右睫毛四
            eyelash(ctx1, 100, 105, 115, 127, 128, 125, "#111")

            eyelash(ctx1, 103, 102, 115, 122, 128, 124, "white")

            // 右睫毛五
            eyelash(ctx1, 83, 111, 92, 135, 102, 132, "#111")

            eyelash(ctx1, 86, 108, 92, 130, 102, 132, "white")

            // 右睫毛六
            eyelash(ctx1, 77, 105, 64, 127, 52, 128, "#111")

            eyelash(ctx1, 74, 102, 62, 122, 54, 127, "white")

            // 右睫毛七
            eyelash(ctx1, 60, 95, 45, 117, 28, 117, "#111")

            eyelash(ctx1, 57, 92, 45, 112, 28, 116, "white")

            // 右睫毛八
            eyelash(ctx1, 30, 89, 32, 101, 14, 100, "#111")

            eyelash(ctx1, 30, 87, 32, 97, 14, 99, "white")

            // 右下弯眼
            eyelash(ctx1, 15, 85, 85, 145, 165, 85, "#111")

            eyelash(ctx1, 15, 80, 85, 135, 162, 85, "white")

            break;

        case 1: //睁眼
            // 右眼
            eyelid(ctx1, 100, 85, 70, 80, 0, 0, Math.PI * 2, "#111")

            //绘制右眼球
            eyeball(ctx1, 120, 55, 25, 0, 2 * Math.PI, "#ddd")

            eyeball(ctx1, 80, 135, 10, 0, 2 * Math.PI, "#ddd")

            // 绘制右眼神光
            eyeball(ctx1, 135, 50, 5, 0, 2 * Math.PI, "#fff")

            eyeball(ctx1, 127, 40, 3, 0, 2 * Math.PI, "#fff")

            break;

        case 2:
            // 眨眼
            // 右眼
            wink(ctx1, "round", 150, 30, 50, 80, 150, 130, 9, "#000")

            break;
    }
}

// 嘴巴
var mouth = function(i) {

    var ctx2 = myCanvas2.getContext('2d');
    ctx2.clearRect(0, 0, 200, 170); //清画布

    switch (i) {
        case 0:
            // 微笑
            smile(ctx2, 50, 30, 50, 110, 150, 110, 150, 30, "#ff3333", "#c00", 4, "round")

            break;

        case 1:
            smile(ctx2, 30, 30, 30, 100, 170, 100, 170, 30, "#ff3333", "#c00", 4, "round")

            break;

        case 2:
            // 张嘴
            openmouth(ctx2, 72, 38, 72, 91, 125, 91, 125, 38, "#ff3333") // 填充
            mouthLeft(ctx2, 75, 37, 25, 20, 15, 80, 75, 90, "#ff3333", "#990000", 4) // 左
            mouthLeft(ctx2, 125, 36, 175, 20, 185, 80, 125, 90, "#ff3333", "#990000", 4) // 右
            mouthTop(ctx2, 72, 36, 94, 43, 125, 36, "#990000", 4) // 上
            mouthTop(ctx2, 72, 90, 94, 95, 125, 90, "#990000", 4) // 下
            break;

        case 3:
            // 张嘴
            // 填充
            openmouth(ctx2, 72, 17, 44, 110, 151, 110, 126, 17, "#ff3333");
            tongue(ctx2, 46, 110, 100, 70, 150, 110, "#ff6666"); // 舌头
            mouthLeft(ctx2, 75, 17, 25, 0, 15, 50, 47, 111, "#ff3333", "#990000", 4); // 左
            mouthLeft(ctx2, 125, 16, 175, 0, 185, 50, 150, 110, "#ff3333", "#990000", 4); // 右
            mouthTop(ctx2, 72, 16, 94, 23, 125, 16, "#990000", 4); // 上
            mouthBottom(ctx2, 46.5, 110, 100, 185, 150, 110, "#990000", 4, "#ff6666"); // 下
            break;

        case 4:
            // 惊讶
            shock(ctx2, 100, 70, 25, 35, 0, 0, 2 * Math.PI, 15, "#993333")
            break;
    }
}

var biaoqing = {
    // 眨眼
    zhayan: function(zy) {
        if (!zy) {
            leftEye(0);
            rightEye(0);
            mouth(0);
            zy = 1;
        } else {
            leftEye(1);
            rightEye(1);
            mouth(3);
            zy = 0;
            return false;
        }
        setTimeout(() => {
            biaoqing.zhayan(zy)
        }, 1000);
    }
}

function newFunction() {
    leftEye(1);
    rightEye(1);
    mouth(2);
    soundWave();
    halfEar();
    sideFace();
}

newFunction()

var Init = function() {
    setInterval(() => {
        biaoqing.zhayan()
    }, 3000);
}

Init();