// upc_tools javascript

function ajax_upc_lookup(source_dom, target_dom) {
    source = getElement(source_dom);
    target = getElement(target_dom);
    code = source.value;
    target.innerHTML = '<img src="/tg_widgets/upc_tools_static/spinner.gif">';
    remoteRequest('', '/upc_tools/?code=' + code, target_dom, Array(), []);
}