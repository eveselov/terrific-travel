/*
 * Terrific Travel: default web client layout.
 *
 * Replaces Evennia's evennia/web/static/webclient/js/plugins/goldenlayout_default_config.js
 * (same path, so Django's static files from the game directory win). It adds a "Map" pane on
 * the right, which only takes messages of type "map" and replaces its content each time.
 *
 * GoldenLayout remembers the last layout in the browser's localStorage, which would hide a
 * changed default from returning players. LAYOUT_VERSION forgets that saved layout once
 * whenever it changes: bump it when this file changes.
 */
(function () {
    var LAYOUT_VERSION = "terrific-travel-1";
    try {
        if (localStorage.getItem("terrificTravelLayoutVersion") !== LAYOUT_VERSION) {
            localStorage.removeItem("evenniaGoldenLayoutSavedState");
            localStorage.removeItem("evenniaGoldenLayoutSavedStateName");
            localStorage.setItem("terrificTravelLayoutVersion", LAYOUT_VERSION);
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
                width: 60, // percentage
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
                type: "component",
                componentName: "evennia",
                title: "Map",
                width: 40, // percentage
                tooltip: "Map - drag to desired position.",
                componentState: {
                    types: "map",
                    updateMethod: "replace",
                },
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
