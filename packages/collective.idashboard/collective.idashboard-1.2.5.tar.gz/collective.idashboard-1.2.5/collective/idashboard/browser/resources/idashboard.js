/*-------------------------------------------------------------------- 
 * "pxToEm"
 * by: Scott Jehl, Maggie Wachs (http://www.filamentgroup.com)
 *
 * Everything else by JC Brand, jc@opkode.com
 *
 * Licensed under GPL (http://www.opensource.org/licenses/gpl-license.php)
 * 
--------------------------------------------------------------------*/
$ = jq;

var drag_and_drop = {

    settings : {
        columns : '.column',  
        widgetSelector: '.widget',  
        handleSelector: '.portletHeader',  
        contentSelector: '.portletItem',  
        portlets: '.draggable'
    },

    init : function() {
        this.setupPortletControls();
        this.setupDragAndDrop();  
    },

    setupPortletControls : function() {
        var settings = this.settings;
        var portlets = $(settings.portlets, top.document);
        portlets.css({'cursor':'move'}).each(function(i) {
            var hash = $(this).attr('hash');
            var controls = $('#portlet-controls-'+hash, top.document);
            var portlet_header = $('#portletbody-'+hash+' .portletHeader', top.document);
            portlet_header.prepend(controls.show());
        });
    },

    setupDragAndDrop : function () {  
        var instance = this;
        var settings = this.settings;
        var columns = $(settings.columns, top.document);
        columns.sortable({
            connectWith: columns,
            handle: settings.handleSelector,
            placeholder: 'portlet-placeholder',
            forcePlaceholderSize: true,
            revert: 300,
            delay: 100,
            opacity: 0.6,
            containment: 'document',
            stop: function (e,ui) {
                instance.movePortlet(ui);
                columns.sortable('enable');
            }
        });
        columns.disableSelection();
    },

    movePortlet : function(ui) {
        $('.portlets-manager').equaliseColumns();
        var portlet = $(ui.item.context);
        var manager_name = $(ui.item.context.parentNode).attr('id');
        var portlet_hash = portlet.attr('hash');
        var prev_id = portlet.prev().attr('id');
        if (prev_id == undefined)
            prev_id = ''
        $.post("@@movePortlet", {
                    portlethash: portlet_hash,
                    manager: manager_name,
                    prev_id: prev_id
                }, 
                function(hash) { 
                    portlet.attr('hash', hash);
                    portlet.attr('id', 'portletwrapper-' + hash)
                } 
            ); 
    }
};

togglePortlet = function(node, hash) {
    var portlet = $(node).parents('.dp-portlet');
    portlet.find('dd.portletItem, dd.portletFooter').slideToggle(300);
    var toggle_icon = $('#portlet-toggle-'+hash);
    toggle_icon.toggleClass("min-dashboard-portlet");
    toggle_icon.toggleClass("max-dashboard-portlet");
},

removePortlet = function(node) {
    node = $(node);
    var portlet = node.parents('.dp-portlet');
    var hash = portlet.attr('hash');
    var confirm_title = node.attr('confirm_title');
    var confirm_message = node.attr('confirm_message');
    jConfirm(confirm_message, confirm_title, 
            function(result) {
                if (result == true) {
                    $.post("@@removePortlet", {
                            portlethash: hash
                        }, 
                        function() {} 
                    ); 
                    $('#portletwrapper-'+hash).fadeOut(500);
                }
            });
}

configurePortlet = function(node) {
    var portlet = $(node).parents('.dp-portlet');
    var hash = portlet.attr('hash');
    $.post("@@configurePortlet", {
            portlethash: hash
        }, 
        function(html) {
            portlet.after(html);
            portlet.hide(300);
            var hash = portlet.attr('hash');
            var iframe = $('iframe#iframe-'+hash);
            iframe.load(function() 
            {
                $(this).fadeIn(1000);
                // var height = parseInt(this.contentWindow.document.body.offsetHeight) + 20
                var height = this.contentWindow.document.body.scrollHeight;
                this.height = height + 'px';
                this.style.height = height + 'px';
                var form = $('#iframe-form-wrapper-'+hash+' form', $(this).contents());
                form.submit(submitPortletEditForm); 
                $('div#iframe-spinner').fadeOut(300);
            });

        } 
    ); 
},

cancelPortletEditForm = function(hash) {
    var portlet = $('#portletwrapper-'+hash, parent.document.body);
    portlet.fadeIn(500);
    var portlet_edit = $('#portleteditwrapper-'+hash, parent.document.body);
    portlet_edit.fadeOut(500)
    portlet_edit.remove(1000)
}

submitPortletEditForm = function(evnt) {
    var hash = evnt.currentTarget.portlethash.value;
    var iframe = $('iframe#iframe-'+hash);
    var form = $('#iframe-form-wrapper-'+hash+' form', iframe.contents());
    var formhash = form.formHash();
    var formmap = {};
    for (x in formhash) {
        formmap[x] = formhash[x];
    }
    $.post("@@submitPortletEditForm", 
        formmap,
        function(html) {
            var oldportlet = $('#portletwrapper-'+hash, parent.document.body);
            oldportlet.replaceWith(html).ready(function() {
                drag_and_drop.init();
            });

            var portlet_edit = $('#portleteditwrapper-'+hash, parent.document.body);
            portlet_edit.remove();
        } 
    ); 
    return false;
},

$.fn.equaliseColumns = function(px) {
    var highest_column = 0; 
    var current_column = 0;

    $(this).each(function(i) {
        current_column = 0;
        $(this).children().each(function(){
            current_column += $(this).height();
        });
        if (current_column > highest_column) {
            highest_column = current_column;
        }
    });

    $(this).each(function(i){
        // for ie6, set height since min-height isn't supported
        if ($.browser.msie && $.browser.version == 6.0) { 
            $(this).css({'height': highest_column.pxToEm()}); 
        }
        $(this).css({'min-height': highest_column.pxToEm()}); 
    });
    return this;
};


Number.prototype.pxToEm = String.prototype.pxToEm = function(settings){
    //set defaults
    settings = jQuery.extend({
        scope: 'body',
        reverse: false
    }, settings);
    
    var pxVal = (this == '') ? 0 : parseFloat(this);
    var scopeVal;
    var getWindowWidth = function(){
        var de = document.documentElement;
        return self.innerWidth || (de && de.clientWidth) || document.body.clientWidth;
    };	
    
    /* When a percentage-based font-size is set on the body, IE returns that 
     * percent of the window width as the font-size. For example, if the body 
     * font-size is 62.5% and the window width is 1000px, IE will return 625px 
     * as the font-size. When this happens, we calculate the correct body 
     * font-size (%) and multiply it by 16 (the standard browser font size) 
     * to get an accurate em value. */
                
    if (settings.scope == 'body' && $.browser.msie && (parseFloat($('body').css('font-size')) / getWindowWidth()).toFixed(1) > 0.0) {
        var calcFontSize = function(){		
            return (parseFloat($('body').css('font-size'))/getWindowWidth()).toFixed(3) * 16;
        };
        scopeVal = calcFontSize();
    }
    else { scopeVal = parseFloat(jQuery(settings.scope).css("font-size")); };
            
    var result = (settings.reverse == true) ? (pxVal * scopeVal).toFixed(2) + 'px' : (pxVal / scopeVal).toFixed(2) + 'em';
    return result;
};


