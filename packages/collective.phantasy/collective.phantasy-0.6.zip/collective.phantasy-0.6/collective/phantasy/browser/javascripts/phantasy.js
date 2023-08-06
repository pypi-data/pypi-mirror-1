// temp hack of formTabs threshold to get standard behavior with more
// than 6 tabs in Phantasy Skin edit form
buildTabs31X = function(container, legends) {
    var threshold = 10;
    var tab_ids = [];
    var panel_ids = [];

    legends.each(function(i) {
        tab_ids[i] = '#' + this.id;
        panel_ids[i] = tab_ids[i].replace(/^#fieldsetlegend-/, "#fieldset-");
    });
    var handler = ploneFormTabbing._toggleFactory(
        container, tab_ids.join(','), panel_ids.join(','));

    if (legends.length > threshold) {
        var tabs = document.createElement("select");
        var tabtype = 'option';
        jq(tabs).change(handler).addClass('noUnloadProtection');
    } else {
        var tabs = document.createElement("ul");
        var tabtype = 'li';
    }
    jq(tabs).addClass('formTabs');

    legends.each(function() {
        var tab = document.createElement(tabtype);
        jq(tab).addClass('formTab');

        if (legends.length > threshold) {
            jq(tab).text(jq(this).text());
            tab.id = this.id;
            tab.value = '#' + this.id;
        } else {
            var a = document.createElement("a");
            a.id = this.id;
            a.href = "#" + this.id;
            jq(a).click(handler);
            var span = document.createElement("span");
            jq(span).text(jq(this).text());
            a.appendChild(span);
            tab.appendChild(a);
        }
        tabs.appendChild(tab);
        jq(this).remove();
    });
    
    jq(tabs).children(':first').addClass('firstFormTab');
    jq(tabs).children(':last').addClass('lastFormTab');
    
    return tabs;
};





if (typeof jq != "undefined") {
    // patch plone method ploneFormTabbing._buildTabs
    ploneFormTabbing._buildTabs = buildTabs31X ;
}
   
