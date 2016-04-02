(function () {
    "use strict";

    var Library = function () {
        var self = this;
        self.version = "0.1.0";
        self.name = "RealTime";
        self.websocket = null;
        self.vm = null;

        function Person (id, sitting) {
            var self = this;
            self.id = id;
            self.sitting = sitting;

            if (self.sitting === undefined) {
                self.sitting = false;
            }
            self.sitting = ko.observable(self.sitting);
            self.format = "Person " + self.id;

            self.cssState = ko.pureComputed(function () {
                var css = "list-group-item list-group-item-";
                if (self.sitting()) {
                    return css + "success";
                }
                return css + "danger";
            }, self);
        }

        /**
         * ViewModel representing this plugin's data
         *
         * @param {String}  uri     Target uri for data updates
         * @param {Object}  data    Data representing plugin (files, channels, groups)
         * @constructor
         */
        function ViewModel (uri, data) {
            console.info("Creating ViewModel");
            var self = this;
            self.uri = uri;
            self.people = ko.observableArray();
        }

        self.wsOnOpen = function () {
            console.debug("Connection opened")
        };

        self.wsOnClose = function () {
            console.debug("Connection closed")
        };

        self.wsOnError = function (error) {
            console.error("Websocket error: " + error);
            console.debug(error)
        };

        self.wsOnMessage = function (e) {
            console.debug("Got msg");
            var data = e.data;
            var i, p;

            if ($.type(data) === "string") {
                data = $.parseJSON(data);
            }

            if (data.event == "person_new") {
                console.debug("Adding people");
                for (i = 0; i < data.people.length; i++) {
                    p = data.people[i];
                    self.vm.people.push(new Person(p.id, p.sitting));
                }
            } else if (data.event == "person_leave") {
                console.debug("Removing people");
                for (i = 0; i < data.people.length; i++) {
                    p = data.people[i];
                    self.vm.people.remove(function (item) {
                        console.debug(item.id + "==" + p.id);
                        return item.id == p.id;
                    });
                }
            } else if (data.event == "person_update") {
                console.debug("Updating people");
                for (i = 0; i < data.people.length; i++) {
                    p = data.people[i];

                    for (var j = 0; j < self.vm.people().length; j++) {
                        var p2 = self.vm.people()[j];
                        if (p.id == p2.id) {
                            p2.sitting(p.sitting);
                            break;
                        }
                    }
                }
            } else {
                console.error("Unknown event occured");
            }
        };

        self.createVM = function (uri, data) {
            self.vm = new ViewModel(uri, data);
        };

        /**
         * Called when all resources have been loaded
         *
         * @param {String} plugin_name Name of loaded plugin (should be equal to .name)
         * @param {String} uri   Uri to post data changes to
         * @param {object} data  Initial/setup data
         */
        self.enter = function (plugin_name, uri, data) {
            console.info(plugin_name + " is ready");
            if ($.type(data) === "string") {
                data = $.parseJSON(data);
            }
            //data.websocket = "ws://localhost:2346";
            if ("WebSocket" in window) {
               self.websocket = new WebSocket(data.websocket);
            } else if ("MozWebSocket" in window) {
               self.websocket = new MozWebSocket(data.websocket);
            } else {
               log("Browser does not support WebSocket!");
               window.location = "http://autobahn.ws/unsupportedbrowser";
            }

            if (self.websocket) {
                self.websocket.onopen = self.wsOnOpen;
                self.websocket.onclose = self.wsOnClose;
                self.websocket.onerror = self.wsOnError;
                self.websocket.onmessage = self.wsOnMessage;
            }

            if (self.vm == null) {
                // create model
                console.debug(plugin_name + " created");
                self.createVM(uri, data);
                ko.applyBindings(self.vm, $("#audplugin_realtime")[0]);
            }
        };

        /**
         * Called when plugin is being unloaded
         *
         * @param {String} plugin_name Name of plugin being unloaded (should be equal to .name)
         */
        self.exit = function (plugin_name) {
            console.info(plugin_name + " is being unloaded");
            self.websocket.close();
            self.websocket = null;
            ko.cleanNode($("#audplugin_realtime")[0]);
            self.vm = null;
            delete window.AUDPlugin_realtime;
        };

        /**
         * Function to send data changes to active plugin
         *
         * @param {String} widget    Widget name updating
         * @param {object} data      Changed data
         * @returns {object | undefined} Value passed to AUDWidget_*
         */
        this.widgetDataSet = function (widget, data) {
            console.info(widget + " is updating data");
            return;
        };

        // Return as object
        return self;
    };

    if (!window.AUDPlugin_realtime) {
        window.AUDPlugin_realtime = new Library();
    }

    // Plugin loaded -> register with AUDPlugin
    AUDPlugin.plugin_register(AUDPlugin_realtime);
})();
