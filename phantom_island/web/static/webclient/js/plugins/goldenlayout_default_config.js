/*
 * Phantom Island: default web client layout.
 *
 * Replaces Evennia's evennia/web/static/webclient/js/plugins/goldenlayout_default_config.js
 * (same path, so Django's static files from the game directory win). Main text on the left;
 * on the right the Map pane above the Focus pane (the room's picture). Both take only their
 * own message type and replace their content each time (see panes.js).
 *
 * GoldenLayout remembers the last layout in the browser's localStorage, which would hide a
 * changed default from returning players. LAYOUT_VERSION forgets that saved layout once
 * whenever it changes: bump it when this file changes.
 */
(function () {
    var LAYOUT_VERSION = "phantom-island-1";
    try {
        if (localStorage.getItem("phantomIslandLayoutVersion") !== LAYOUT_VERSION) {
            localStorage.removeItem("evenniaGoldenLayoutSavedState");
            localStorage.removeItem("evenniaGoldenLayoutSavedStateName");
            localStorage.setItem("phantomIslandLayoutVersion", LAYOUT_VERSION);
        }
    } catch (e) {
        // localStorage can be blocked (private windows); the default layout is used anyway.
    }
})();

var goldenlayout_config = { // Global Variable used in goldenlayout.js init()
    content: [{
        type: "column",
        content: [{
            type: "row",
            content: [{
                type: "column",
                width: 58, // percentage
                content: [{
                    type: "component",
                    componentName: "Main",
                    isClosable: false,
                    tooltip: "Main - drag to desired position.",
                    componentState: {
                        types: "untagged",
                        updateMethod: "newlines",
                    },
                }]
            }, {
                type: "column",
                width: 42, // percentage
                content: [{
                    type: "component",
                    componentName: "evennia",
                    title: "Map",
                    height: 55, // percentage
                    tooltip: "Map - drag to desired position.",
                    componentState: {
                        types: "map",
                        updateMethod: "replace",
                    },
                }, {
                    type: "component",
                    componentName: "evennia",
                    title: "Focus",
                    height: 45, // percentage
                    tooltip: "Focus - drag to desired position.",
                    componentState: {
                        types: "focus",
                        updateMethod: "replace",
                    },
                }]
            }],
        }, {
            type: "component",
            componentName: "input",
            id: "inputComponent", // mark 'ignore this component during output message processing'
            height: 20,  // percentage
            isClosable: false,
            tooltip: "Input - The last input in the layout is always the default.",
        }]
    }]
};
