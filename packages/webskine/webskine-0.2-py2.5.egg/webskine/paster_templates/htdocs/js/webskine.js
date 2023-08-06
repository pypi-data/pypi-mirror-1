/*
 * Webskine administrator interface.
 *   http://dealmeida.net/projects/webskine
 *
 * This module is a client to my JSON store module, creating,
 * editing and deleting Atom entries.
 *
 * Copyright (c) 2006 Roberto De Almeida
 * Licensed under the MIT License:
 *   http://www.opensource.org/licenses/mit-license.php
 */

String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, "");
};

// Initialize the tinyMCE instance.
tinyMCE.init({
    mode: "none",
    theme: "advanced",
    theme_advanced_buttons1: "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect,fontsizeselect",
    theme_advanced_buttons2: "cut,copy,paste,pastetext,pasteword,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,forecolor,backcolor",
    valid_elements: "*[*]",
    width: "100%",
    content_css: "/css/style.css",
    strict_loading_mode : true
});
var editorCount = 0;

/*
 * A JSON request, loosely based on http://www.json.org/JSONRequest.html.
 *
 * We could use http://json.org/json.js for parsing the JSON response,
 * but it hangs Firefox.
 */
$.json = function(type, url, data, ret) {
    var xml = new XMLHttpRequest();

    if (xml) {
        xml.open(type || "GET", url, true);

        if (data) xml.setRequestHeader('Content-Type', 'application/json');

        xml.onreadystatechange = function() {
            if (xml.readyState == 4) {
                if (ret) {
                    eval('var jsonResponse = ' + (xml.responseText || null) + ';');
                    ret(jsonResponse);
                }
            }
        };
        xml.send(toJsonString(data));
    }
};

// Activate existing entries.
$.fn.activate = function() {
    return this.each(function() {
        var me = this;

        // Get the title.
        var title = $(me).find(".title").html();

        // Create a div for the buttons.
        var menu = document.createElement("div");
        $(menu).addClass("menu");
        $(me).before(menu);

        // Add an edit button.
        var y = document.createElement("img");
        y.src = "images/edit.png";
        y.title = "Edit post '" + title + "'";
        y.style.cursor = "pointer";
        $(y).click(function() {
            // Edit entry.
            if (!me.editing) $(me).edit();
        });
        $(menu).append(y);
        $(menu).append('&nbsp;');
        
        // Add a delete button.
        var x = document.createElement("img");
        x.src = "images/delete.png";
        x.title = "Delete post '" + title + "'";
        x.style.cursor = "pointer";
        $(x).click(function() {
            if (confirm("Are you sure you want to delete the post '" + title + "'?")) {
                $.json("DELETE", jsonStore + me.id, true, function(json) {
                    $(me).hide("slow");
                    $(menu).remove();
                });
            }
        });
        $(menu).append(x);
    });
};

// Make entry editable.
$.fn.edit = function() {
    return this.each(function() {
        var me = this;
        me.editing = true;

        // Get original HTML, title and content.
        me.html = $(me).html();
        me.title = $(me).find(".title").html();
        me.content = $(me).find(".content").html();

        // Trim content.
        me.content = me.content.trim();

        // Clear div (but keep menu).
        $(me).html('');

        // Edit title.
        var title = document.createElement("input");
        title.value = me.title;
        title.style.width = "100%";
        $(me).append(title);
        $(me).append("<br/>");

        // Edit content.
        var content = document.createElement("textarea");
        content.id = "content" + (editorCount++);
        content.value = me.content;
        content.rows = 20;
        content.style.width = "100%";
        $(me).append(content);
        $(me).append("<br/>");
        
        // Add rich text editor.
        tinyMCE.execCommand('mceAddControl', true, content.id);
        
        // Discard button.
        var discard = document.createElement("input");
        discard.type = "button";
        discard.value = "Discard changes";
        $(discard).click(function() {
            if (me.id) {
                // Existing post.
                me.innerHTML = me.html;
            } else {
                $(me).hide("slow");
            }
            me.editing = false;
        });
        $(me).append(discard);

        // Post button.
        var post = document.createElement("input");
        post.type = "button";
        post.value = "Post entry";
        $(post).click(function() {
            var entry = {};
            entry.title = title.value;
            entry.content = {'content': tinyMCE.getContent()};
            if (me.id) {
                entry.id = me.id;
                url = jsonStore + me.id;
                method = 'PUT';
            } else {
                url = jsonStore;
                method = 'POST';
            }

            $.json(method, url, entry, function(json) {
                var html = '<h2><a href="' + json.__id__ + '" title="Permalink for this post" class="title">' + json.title + '</a></h2>\n\n' + '<div class="content">\n' + json.content.content + '</div>\n\n<p class="footnote">Updated ' + json.__updated__ + '</p>\n\n<p class="break">❁</p>';
                me.innerHTML = html;

                // Activate new entry for editing.
                if (!me.id) {
                    $(me).activate();
                    me.id = json.__id__;
                }
            });
        
            me.editing = false;
        });
        $(me).append(post);

        // Add break.
        $(me).append('<p class="break">❁</p>');
    });
};

// Add admnistrative buttons.
function init() {
    // Add new post button.
    var x = document.createElement("img");
    x.src = "images/add.png";
    x.title = "Add a new post";
    x.style.cursor = "pointer";
    $(x).click(function() {
        // Create a new dummy post.
        var div = document.createElement("div");
        $(div).addClass("entry");
        $(div).hide();

        // Create placeholders.
        $(div).append('<h2 class="title">Title</h2>');
        $(div).append('<div class="content"><p>Type entry here...</p></div>');

        // Edit entry.
        $(x).after(div);
        $(div).edit();
        
        // Show entry.
        $(div).show("slow");
    });
    $("div#main").prepend(x);
    
    // Add delete/edit buttons for each post.
    $("div.entry").activate();
};

$(document).ready(function() {
    // User is logged?
    if (readCookie("webskine")) {
        init();
    } else {
        // Add a login link. The link does a JSON request to the JSON store,
        // triggering the authentication.
        var link = document.createElement("a");
        link.href = "#";
        link.appendChild(document.createTextNode("login "));
        $(link).addClass("login");
        $(link).click(function() {
            if (!readCookie("webskine")) {
                $.json("GET", jsonStore, true, function(json) {
                    createCookie("webskine", true);
                    init();
                    $(link).remove();
                });
            }
        });
        
        $("div#footer p").append(link);
    }
});
