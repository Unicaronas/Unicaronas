$('.menu .item').tab();

function can_change_tab(tab) {
    var current_div = document.querySelectorAll("[data-tab='" + tab.toString() + "']")[1];
    current_div = $(current_div);
    var required_fields = $(document.querySelectorAll("[data-tab='" + tab.toString() + "']")[1]).find("input").filter('[required]');
    var allow = true;
    required_fields.each(function(field) {
        var value = $(required_fields[field]).val();
        if (!value) {
            $(required_fields[field]).popup({'title': 'Obrigatório!', 'on': 'click', onHide: function(pop) {
                $(required_fields[field]).popup({'on': 'manual'});
            }});
            $(required_fields[field]).popup('show');
        }
        if (value) {
            $(required_fields[field]).popup({'on': 'manual'});
            $(required_fields[field]).popup('hide');
        }
        allow = allow && value;
    });
    return allow;
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
