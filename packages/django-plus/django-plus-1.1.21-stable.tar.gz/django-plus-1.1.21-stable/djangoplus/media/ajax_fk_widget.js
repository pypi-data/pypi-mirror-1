// Dicionário de campos de chave estrangeira controlados pelo widget em Ajax
var fk_widgets = {};

$(document).ready(function(){
    $('input.ajax-fk').each(function(){
        // Display span
        var display = $(this).parent().find('span.ajax-fk-display');

        // Show window icon
        var img = $('<a href="javascript: void(0)" class="ajax-fk-show-window"><img src="/admin_media/img/admin/selector-search.gif"/></a>').insertAfter(display);

        // Add link icon
        if (fk_widgets[$(this).attr('name')]['add-url']) {
            var add = $('<a class="ajax-fk-add" href="javascript: void(0)" title="Adicionar"><img src="/admin_media/img/admin/icon_addlink.gif" alt="Adicionar"/></a>').insertAfter(img);
        } else {
            var add = img;
        }

        // Selection form
        var div = $('<div id="'+$(this).attr('id')+'_window" class="ajax-fk-window"></div>').insertAfter(add);
    }).change(ajax_fk_change);

    $('.ajax-fk-show-window').click(function(){
        $(this).parent().find('.ajax-fk-window').toggle();
        
        if ($(this).parent().find('.ajax-fk-window').css('display') == 'block')
            ajax_fk_load($(this), make_url($(this).parent().find('input:first'), 1));
    });

    $('.ajax-fk-add').click(ajax_fk_add_click);
});

function make_url(input, page) {
    var url = fk_widgets[input.attr('name')]['window-url'] + '?';
    var inputs = input.parent().find('.ajax-fk-filter').find(':input');

    for (var i=0; i<inputs.length; i++) {
        if (!$(inputs[i]).attr('name')) continue
        url += $(inputs[i]).attr('name') + '=' + $(inputs[i]).val() + '&';
    }

    if (page) {
        url += 'page='+page;
    }

    if (fk_widgets[input.attr('name')]['get_additional_params']) {
        url += fk_widgets[input.attr('name')]['get_additional_params']();
    }

    return url;
}

function ajax_fk_search_click() {
    var input = $(this).parent().parent().parent().find('input:first');
    ajax_fk_load(input, make_url(input, 1));
}

function ajax_fk_pagination_click() {
    var params = $(this).attr('href');
    var page = params.match(/^.*[^w]+page=(\d+).*$/)[1];
    var input = $(this).parent().parent().parent().find('input:first');
    var url = make_url(input, page);

    ajax_fk_load(input, url);

    return false;
}

function ajax_fk_row_click() {
    var pk = $(this).find('input#ajax-fk-result-pk').val();
    var display = $(this).find('input#ajax-fk-result-display').val();
    var prnt = $(this).parent().parent().parent().parent().parent();

    prnt.find('input:first').val(pk);
    prnt.find('span.ajax-fk-display').text(display);

    prnt.find('.ajax-fk-window').hide();
}

function ajax_fk_close_click() {
    $(this).parent().parent().hide();
}

function ajax_fk_search_keypress(e) {
    if (e.which == 13) {
        $(this).parent().find('.ajax-fk-search').click();
        return false;
    }
}

function ajax_fk_change() {
    var input = $(this);
    var val = input.val();

    if (!val) {
        input.parent().find('span.ajax-fk-display').text('');
        return;
    }

    var zeros_count = fk_widgets[input.attr('name')]['fill-left-zeros'];
   
    // Fill zeros at left
    for (var i=val.length; i<zeros_count; i++) val = '0' + val;

    // Updates field value
    input.val(val);
 
    // Makes the URL to request
    var url = fk_widgets[input.attr('name')]['load-url'] + '?pk=' + val;

    // Gets foreign object
    $.getJSON(url, function(json){
        if (json['res'] == 'ok') {
            input.parent().find('span.ajax-fk-display').text(json['display']);
        } else {
            alert(json['msg']);
            input.val('');
            input.parent().find('span.ajax-fk-display').text('');
            input.focus();
        }
    });
}

function ajax_fk_add_click() {
    var input = $(this).parent().find('input:first');
    href = fk_widgets[input.attr('name')]['add-url'];
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
}

function ajax_fk_load(input, url) {
    input.parent().find('.ajax-fk-window').load(url, function(){
        $('.pagination').find('a').click(ajax_fk_pagination_click);
        $('input.ajax-fk-search').click(ajax_fk_search_click);
        $('input.#ajax-fk-search').keypress(ajax_fk_search_keypress);
        $('table.ajax-fk-results').find('tbody').find('tr').click(ajax_fk_row_click);
        $('.ajax-fk-close').click(ajax_fk_close_click);

        // Execute post show callback function
        if (fk_widgets[$(this).parent().find('input:first').attr('name')]['post_show_window']) {
            fk_widgets[$(this).parent().find('input:first').attr('name')]['post_show_window']();
        }
    });
}

