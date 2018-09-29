var last_bg = 'bg1';

function init_bg() {
    $('.masthead').removeClass('zoomed');
}

function cycle_db() {
    $('.masthead').removeClass(last_bg);
    var n = Math.floor(Math.random() * 14 + 1);
    last_bg = 'bg' + n;
    $('.masthead').addClass(last_bg); // body...
}

init_bg();


window.setInterval(function(){
    cycle_db();
}, 6000);


function cycle_phrase() {
    var options = [
        "-tretas +caronas",
        "Caronas, só que melhor",
        "Uber da Unicamp",
        "Ônibus tá muito caro",
        "Universitários + caronas = ❤️",
        "Quem tem tempo pra esperar buzão?",
        "Pagamentos em bandecos",
        "Me encontra no posto da 1",
    ]
    var option = options[Math.floor(Math.random() * options.length)];
    $("#masthead_subtitle").text(option);
}

cycle_phrase();
