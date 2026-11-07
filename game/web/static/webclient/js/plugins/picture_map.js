/*
 * Terrific Travel web client plugin: the Map pane and room pictures.
 *
 *     PLUGIN ORDER PREREQS:
 *          loaded after:
 *              webclient_gui.js
 *              goldenlayout.js
 *
 *     Server side (see game/typeclasses/rooms.py):
 *         character.msg(map="<div>...</div>")
 *             replaces the content of every pane whose types include "map";
 *         character.msg(room_image=(("/static/...png",), {"alt": "Harbour"}))
 *             shows a picture in the main text, just before the room description.
 *
 *     The map HTML is built by the server from the game's own data (world/maps.py),
 *     which escapes all text in it.
 */
let picture_map_plugin = (function () {

    // Panes that explicitly asked for map messages. A plain routeMessage() would also send
    // the map to the Main pane whenever the player has closed the Map pane.
    var mapPanes = function () {
        var panes = [];
        var layout = window.plugins["goldenlayout"].getGL();
        layout.root.getItemsByType("component").forEach(function (component) {
            var div = component.container.getElement().children(".content");
            var types = (div.attr("types") || "").split(" ");
            if (types.includes("map")) {
                panes.push(div);
            }
        });
        return panes;
    };

    var onMap = function (args, kwargs) {
        mapPanes().forEach(function (div) {
            div.html(args[0]);
        });
    };

    var scrollToBottom = function (div) {
        div.scrollTop(div.prop("scrollHeight"));
    };

    var onRoomImage = function (args, kwargs) {
        var alt = (kwargs && kwargs["alt"]) || "";
        // Untagged, so it goes where ordinary room text goes (normally the Main pane).
        var panes = window.plugins["goldenlayout"].routeMessage(args, {});
        panes.forEach(function (div) {
            var img = $("<img class='tt-room-image'>").attr({ src: args[0], alt: alt });
            img.on("load", function () { scrollToBottom(div); });
            div.append($("<div class='out'></div>").append(img));
            scrollToBottom(div);
        });
    };

    // Mandatory plugin init function
    var init = function () {
        window.Evennia.emitter.on("map", onMap);
        window.Evennia.emitter.on("room_image", onRoomImage);
        console.log("Picture map plugin initialized");
    };

    return {
        init: init,
    };
})();
window.plugin_handler.add("picture_map", picture_map_plugin);
