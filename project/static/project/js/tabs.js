$('.menu .item').tab();

function can_change_tab(tab) {
    var current_div = $("[data-tab='" + tab.toString() + "']")
    return current_div.isValid('pt');
}

function change_tab(current, target) {
    var current_tab = document.querySelectorAll("[data-tab='" + current.toString() + "']")[0];
    var target_tab = document.querySelectorAll("[data-tab='" + target.toString() + "']")[0];
    var current_div = document.querySelectorAll("[data-tab='" + current.toString() + "']")[1];
    var target_div = document.querySelectorAll("[data-tab='" + target.toString() + "']")[1];
    current_tab.classList.remove("active");
    target_tab.classList.add("active");
    $.tab('change tab', target);
};

function next_tab(current) {
    var target = parseInt(current) + 1;
    var can = can_change_tab(current);
    if (can) {
        change_tab(current.toString(), target.toString());
    }
};

function previous_tab(current) {
    var target = parseInt(current) - 1;
    change_tab(current.toString(), target.toString());
};

function disable_tab(target) {
    var target_tab = $("[data-id='" + target.toString() + "']")[0];
    var span = document.createElement("span");
    var txt = target_tab.text;
    var textNode = document.createTextNode(txt);
    span.appendChild(textNode);
    span.setAttribute("data-id", target);
    span.className += " item";
    span.className += " disabled";
    target_tab.parentNode.replaceChild(span, target_tab);
}

function enable_tab(target) {
    var target_tab = $("[data-id='" + target.toString() + "']");
    var link = document.createElement("a");
    var txt = target_tab.text();
    // var textNode = document.createTextNode(txt);
    link.innerHTML = txt;
    link.setAttribute("data-id", target);
    link.setAttribute("data-tab", target);
    link.className += " item";
    target_tab[0].parentNode.replaceChild(link, target_tab[0]);
    $("[data-id='" + target + "']").tab();
}
