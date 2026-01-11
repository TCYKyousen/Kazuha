"use strict";

var QWebChannelMessageTypes = {
    signal: 1,
    propertyUpdate: 2,
    init: 3,
    idle: 4,
    debug: 5,
    reply: 6,
    error: 7,
    invokeMethod: 8,
    connectToSignal: 9,
    disconnectFromSignal: 10,
    setProperty: 11,
    response: 12,
};

var QWebChannel = function(transport, initCallback)
{
    if (typeof transport !== "object" || typeof transport.send !== "function") {
        console.error("The QWebChannel requires a transport object. This object must implement a send() function.");
        return;
    }

    var channel = this;
    this.transport = transport;

    this.send = function(data)
    {
        if (typeof data !== "string") {
            data = JSON.stringify(data);
        }
        channel.transport.send(data);
    }

    this.transport.onmessage = function(message)
    {
        var data = message.data;
        if (typeof data === "string") {
            data = JSON.parse(data);
        }
        switch (data.type) {
            case QWebChannelMessageTypes.signal:
                channel.handleSignal(data);
                break;
            case QWebChannelMessageTypes.response:
                channel.handleResponse(data);
                break;
            case QWebChannelMessageTypes.propertyUpdate:
                channel.handlePropertyUpdate(data);
                break;
            default:
                console.error("invalid message type received: ", data.type);
                break;
        }
    }

    this.execCallbacks = {};
    this.execId = 0;
    this.exec = function(data, callback)
    {
        if (!callback) {
            channel.send(data);
            return;
        }
        var id = channel.execId++;
        channel.execCallbacks[id] = callback;
        data.id = id;
        channel.send(data);
    };

    this.objects = {};

    this.handleSignal = function(message)
    {
        var object = channel.objects[message.object];
        if (object) {
            object.signalEmitted(message.signal, message.args);
        } else {
            console.warn("Unhandled signal: " + message.object + "::" + message.signal);
        }
    }

    this.handleResponse = function(message)
    {
        if (!message.hasOwnProperty("id")) {
            console.error("Invalid response message received: ", JSON.stringify(message));
            return;
        }
        var callback = channel.execCallbacks[message.id];
        if (callback) {
            delete channel.execCallbacks[message.id];
            callback(message.data);
        }
    }

    this.handlePropertyUpdate = function(message)
    {
        for (var i in message.signals) {
            var signal = message.signals[i];
            var object = channel.objects[signal.object];
            if (object) {
                object.propertyUpdate(signal.signals, signal.properties);
            } else {
                console.warn("Unhandled property update: " + signal.object);
            }
        }
    }

    this.debug = function(message)
    {
        channel.send({type: QWebChannelMessageTypes.debug, data: message});
    };

    this.exec({type: QWebChannelMessageTypes.init}, function(data) {
        for (var objectName in data) {
            var object = new QObject(objectName, data[objectName], channel);
        }
        if (initCallback) {
            initCallback(channel);
        }
        channel.exec({type: QWebChannelMessageTypes.idle});
    });
};

function QObject(name, data, webChannel)
{
    this.__objects__ = [];
    this.__isQObject__ = true;
    webChannel.objects[name] = this;

    this.name = name;
    this.webChannel = webChannel;
    this.signals = {};
    this.properties = {};

    var self = this;

    this.propertyUpdate = function(signals, propertyMap)
    {
        for (var propertyName in propertyMap) {
            var propertyValue = propertyMap[propertyName];
            if (propertyValue && propertyValue.__isQObject__) {
                propertyValue = new QObject(propertyValue.name, propertyValue.data, webChannel);
            }
            self.properties[propertyName] = propertyValue;
            if (signals[propertyName]) {
                var signalName = signals[propertyName];
                var signal = self.signals[signalName];
                if (signal) {
                    signal.emit.apply(signal, [propertyValue]);
                }
            }
        }
    }

    this.signalEmitted = function(signalName, args)
    {
        var signal = self.signals[signalName];
        if (signal) {
            signal.emit.apply(signal, args);
        }
    }

    function createMethod(methodName)
    {
        return function() {
            var args = [];
            var callback;
            for (var i = 0; i < arguments.length; ++i) {
                if (typeof arguments[i] === "function") {
                    callback = arguments[i];
                } else {
                    args.push(arguments[i]);
                }
            }

            webChannel.exec({
                type: QWebChannelMessageTypes.invokeMethod,
                object: self.name,
                method: methodName,
                args: args
            }, callback);
        };
    }

    function createSignal(signalName)
    {
        var signal = {
            connections: [],
            connect: function(callback) {
                if (typeof callback !== "function") {
                    console.error("Internal error: click() argument is not a function: " + callback);
                    return;
                }
                if (signal.connections.indexOf(callback) === -1) {
                    signal.connections.push(callback);
                    if (signal.connections.length === 1) {
                        webChannel.exec({
                            type: QWebChannelMessageTypes.connectToSignal,
                            object: self.name,
                            signal: signalName
                        });
                    }
                }
            },
            disconnect: function(callback) {
                if (typeof callback !== "function") {
                    console.error("Internal error: disconnect() argument is not a function: " + callback);
                    return;
                }
                var index = signal.connections.indexOf(callback);
                if (index !== -1) {
                    signal.connections.splice(index, 1);
                    if (signal.connections.length === 0) {
                        webChannel.exec({
                            type: QWebChannelMessageTypes.disconnectFromSignal,
                            object: self.name,
                            signal: signalName
                        });
                    }
                }
            },
            emit: function() {
                var args = [];
                for (var i = 0; i < arguments.length; ++i) {
                    args.push(arguments[i]);
                }
                for (var i = 0; i < signal.connections.length; ++i) {
                    signal.connections[i].apply(null, args);
                }
            }
        };
        return signal;
    }

    for (var i = 0; i < data.methods.length; ++i) {
        var methodName = data.methods[i][0];
        this[methodName] = createMethod(methodName);
    }

    for (var signalName in data.signals) {
        var signal = createSignal(signalName);
        this.signals[signalName] = signal;
        this[signalName] = signal;
    }

    for (var propertyName in data.properties) {
        this.propertyUpdate({}, data.properties);
    }
}

if (typeof module !== 'undefined') {
    module.exports = {
        QWebChannel: QWebChannel
    };
}
