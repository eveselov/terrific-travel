/*
 * Phantom Island web client plugin: the Map and Focus panes.
 *
 * Copied from the playground's picture_map.js (game/web/static/webclient/js/plugins/) and
 * changed: the room picture goes to its own Focus pane instead of the text scroll.
 *
 *     PLUGIN ORDER PREREQS:
 *          loaded after:
 *              webclient_gui.js
 *              goldenlayout.js
 *
 *     Server side (see phantom_island/typeclasses/rooms.py, Room.send_visuals):
 *         character.msg(map="<div>...</div>")
 *             replaces the content of every pane whose types include "map";
 *         character.msg(focus="<div>...</div>")
 *             replaces the content of every pane whose types include "focus".
 *
 *     The HTML is built by the server from the game's own content files (world/maps.py,
 *     world/focus.py), which escape all text in it.
 *
 *     It also echoes each command the player sends into the Main pane, in its own colour
 *     after a divider line (class "pi-echo", styled in panes.css), so the log shows what
 *     was typed. Telnet clients show what was typed themselves, so the server doesn't echo.
 *     Login lines (connect/create) aren't echoed: they hold a password.
 */
let phantom_island_panes = (function () {

    // Panes that explicitly asked for this message type. A plain routeMessage() would also
    // send it to the Main pane whenever the player has closed the Map or Focus pane.
    var panesFor = function (type) {
        var panes = [];
        var layout = window.plugins["goldenlayout"].getGL();
        layout.root.getItemsByType("component").forEach(function (component) {
            var div = component.container.getElement().children(".content");
            var types = (div.attr("types") || "").split(" ");
            if (types.includes(type)) {
                panes.push(div);
            }
        });
        return panes;
    };

    var replaceIn = function (type) {
        return function (args, kwargs) {
            panesFor(type).forEach(function (div) {
                div.html(args[0]);
            });
        };
    };

    var escapeHtml = function (text) {
        return $("<div>").text(text).html();
    };

    var SECRET = /^\s*@?(connect|create|password)(\s|$)/i;

    // Show the line the player sent in the Main pane. Returns nothing, so the command sent
    // to the server is left unchanged.
    var onSend = function (line) {
        if (!line.trim() || SECRET.test(line)) {
            return;
        }
        window.plugin_handler.onText([escapeHtml(line)], { cls: "pi-echo" });
    };

    // Mandatory plugin init function
    var init = function () {
        window.Evennia.emitter.on("map", replaceIn("map"));
        window.Evennia.emitter.on("focus", replaceIn("focus"));
        console.log("Phantom Island panes plugin initialized");
    };

    return {
        init: init,
        onSend: onSend,
    };
})();
window.plugin_handler.add("phantom_island_panes", phantom_island_panes);
