last_bg = 'bg1';

function preloadImage(source, destElem, newCls, oldCls) {
    var image = new Image();

    image.src = source;

    image.onload = function () {
        $(destElem).removeClass(oldCls);
        $(destElem).addClass(newCls);
        setTimeout(cycle_db, 6000);
    };
}

function init_bg() {
    preloadImage("https://semantic-ui.com/images/backgrounds/1.jpg", '.masthead', 'bg1', 'zoomed');
}

function cycle_db() {
    var n = Math.floor(Math.random() * 14 + 1);
    new_bg = 'bg' + n;
    url = "https://semantic-ui.com/images/backgrounds/" + n + '.jpg';
    preloadImage(url, '.masthead', new_bg, last_bg);
    last_bg = 'bg' + n;
}

init_bg();


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
