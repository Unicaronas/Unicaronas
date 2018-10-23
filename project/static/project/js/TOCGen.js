var toc_counter = 0;

function find_children(element, level) {
    return $(element).find('h' + level);
}

function find_nexts(element, level) {
    return $(element).nextUntil('h' + (level - 1), 'h' + level);
}

function recurse_headers(element, level) {
    $(element).attr('id', 'toc_item_' + toc_counter);
    var item = '<div class="item"><a href="#toc_item_' + toc_counter++ + '">'+ '&nbsp;&nbsp;'.repeat(level - 1) + $(element).text() + '</a>';
    var children = find_nexts(element, level + 1);

    if (children.length != 0) {
        item += '<div class="list">';
        children.each(function(index) {
            item +=  recurse_headers(this, level + 1);
        });
        item += '</div>';
    }
    item += '</div>';
    return item;
}

function generate_toc(parent_id, target_id) {
    var parent = $('#' + parent_id);
    var target = $('#' + target_id);

    var children = find_children(parent, 1);

    var toc = '<div class="ui ordered list">';
    children.each(function(index) {
        toc += recurse_headers(this, 1) ;
    })
    toc += '</div>';
    target.append(toc);
}
