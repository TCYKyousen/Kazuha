"use strict";

var QWebChannelMessageTypes = {
    signal: 1,
    propertyUpdate: 2,
    init: 3,
    idle: 4,
    debug: 5,
    invokeMethod: 6,
    connectToSignal: 7,
    disconnectFromSignal: 8,
    setProperty: 9,
    response: 10,
};

var QWebChannel = function(transport, initCallback)
{
    if (typeof transport !== "object" || typeof transport.send !== "function") {
        console.error("The QWebChannel expects a transport object with a send function and onmessage callback property." +
                      " Given is: transport: " + typeof(transport) + ", transport.send: " + typeof(transport.send));
        return;
    }

    var channel = this;
    this.transport = transport;

    this.send = function(data)
    {
        if (typeof(data) !== "string") {
            data = JSON.stringify(data);
        }
        channel.transport.send(data);
    }

    this.execCallbacks = {};
    this.execId = 0;
    this.execCallbacks[0] = [];

    this.objects = {};

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
                console.error("invalid message received:", message.data);
                break;
        }
    }

    this.exec = function(data, callback)
    {
        if (!callback) {
            // if no callback is given, send the signal immediately
            channel.send(data);
            return;
        }

        if (channel.execId === Number.MAX_VALUE) {
            // wrap
            channel.execId = Number.MIN_VALUE;
        }
        if (data.hasOwnProperty("id")) {
            console.error("Cannot exec message with property id: " + JSON.stringify(data));
            return;
        }
        data.id = channel.execId;
        channel.execCallbacks[channel.execId] = callback;
        channel.execId++;
        channel.send(data);
    };

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
        channel.execCallbacks[message.id](message.data);
        delete channel.execCallbacks[message.id];
    }

    this.handlePropertyUpdate = function(message)
    {
        for (var i in message.data) {
            var data = message.data[i];
            var object = channel.objects[data.object];
            if (object) {
                object.propertyUpdate(data.signals, data.properties);
            } else {
                console.warn("Unhandled property update: " + data.object + "::" + data.signal);
            }
        }
        channel.execCallbacks[0](message.data);
        delete channel.execCallbacks[0];
    }

    this.debug = function(message)
    {
        channel.send({type: QWebChannelMessageTypes.debug, data: message});
    };

    channel.exec({type: QWebChannelMessageTypes.init}, function(data) {
        for (var objectName in data) {
            var object = new QObject(objectName, data[objectName], channel);
        }
        // now unwrap properties, which might reference other registered objects
        for (var objectName in channel.objects) {
            channel.objects[objectName].unwrapProperties();
        }
        if (initCallback) {
            initCallback(channel);
        }
        channel.execCallbacks[0] = [];
    });
};

function QObject(name, data, webChannel)
{
    this.__id__ = name;
    webChannel.objects[name] = this;

    // List of callbacks that get invoked upon signal emission
    this.__objectSignals__ = {};

    // Cache of all properties, updated when a notify signal is emitted
    this.__propertyCache__ = {};

    var object = this;

    // ----------------------------------------------------------------------
    // properties
    this.unwrapProperties = function()
    {
        for (var propertyIndex in data.properties) {
            object.unwrapProperty(propertyIndex);
        }
    }

    this.unwrapProperty = function(propertyIndex)
    {
        var propertyName = data.properties[propertyIndex][0];
        var propertyValue = data.properties[propertyIndex][1];

        // generate getter/setter, loosely based on Qt's qmlweb
        if (!object.hasOwnProperty(propertyName)) {
            Object.defineProperty(object, propertyName, {
                configurable: true,
                get: function () {
                    var propertyValue = object.__propertyCache__[propertyIndex];
                    if (propertyValue === undefined) {
                        // This shouldn't happen
                        console.warn("Undefined value in property: " + propertyName + " in object: " + name);
                    }
                    return propertyValue;
                },
                set: function(value) {
                    if (value === undefined) {
                        console.warn("Property setter: " + propertyName + " in object: " + name + " with undefined value");
                        return;
                    }
                    var current = object.__propertyCache__[propertyIndex];
                    // compare property values, avoiding loops
                    if (current === value) {
                        return;
                    }
                    object.__propertyCache__[propertyIndex] = value;
                    webChannel.exec({
                        type: QWebChannelMessageTypes.setProperty,
                        object: name,
                        property: propertyIndex,
                        value: value
                    });
                }
            });
        }

        object.__propertyCache__[propertyIndex] = propertyValue;

        // find notify signal
        for (var signalName in data.signals) {
            var signal = data.signals[signalName];
            var signalIndex = signal[0];
            if (signalIndex === data.properties[propertyIndex][2]) {
                object[signalName].connect(function() {
                    var newValue = object.__propertyCache__[propertyIndex];
                    // update cache, if property value is not yet up-to-date
                    // this happens when the change is triggered by the backend
                    if (newValue !== object[propertyName]) {
                         object.__propertyCache__[propertyIndex] = object[propertyName];
                    }
                });
            }
        }
    }

    this.propertyUpdate = function(signals, properties)
    {
        // update property cache
        for (var propertyIndex in properties) {
            var propertyValue = properties[propertyIndex];
            object.__propertyCache__[propertyIndex] = propertyValue;
        }

        // emit signals
        for (var signalName in signals) {
            var signal = object[signalName];
            var signalIndex = data.signals[signalName][0];
            var args = signals[signalName];
            object.signalEmitted(signalIndex, args);
        }
    }

    this.signalEmitted = function(signalIndex, signalArgs)
    {
        var signal = object.__objectSignals__[signalIndex];
        if (signal) {
            signal.fire(signalArgs);
        }
    }

    // ----------------------------------------------------------------------
    // signals
    this.unwrapSignals = function()
    {
        for (var signalName in data.signals) {
            object.unwrapSignal(signalName);
        }
    }

    this.unwrapSignal = function(signalName)
    {
        var signalIndex = data.signals[signalName][0];
        var signal = new QSignal(object, signalIndex, webChannel);
        object[signalName] = signal;
        object.__objectSignals__[signalIndex] = signal;
    }

    // ----------------------------------------------------------------------
    // methods
    this.unwrapMethods = function()
    {
        for (var methodName in data.methods) {
            object.unwrapMethod(methodName);
        }
    }

    this.unwrapMethod = function(methodName)
    {
        object[methodName] = function() {
            var args = [];
            var callback;
            for (var i = 0; i < arguments.length; i++) {
                if (typeof arguments[i] === "function") {
                    callback = arguments[i];
                } else {
                    args.push(arguments[i]);
                }
            }

            webChannel.exec({
                "type": QWebChannelMessageTypes.invokeMethod,
                "object": name,
                "method": data.methods[methodName][0],
                "args": args
            }, function(response) {
                if (response !== undefined) {
                    var result = response;
                    if (callback) {
                        callback(result);
                    }
                }
            });
        };
    }

    this.unwrapProperties();
    this.unwrapSignals();
    this.unwrapMethods();
}

function QSignal(sender, signalIndex, webChannel)
{
    this.connect = function(callback)
    {
        if (typeof callback !== "function") {
            console.error("Bad callback given to connect to signal " + sender.__id__ + "::" + signalIndex);
            return;
        }

        this.observers[this.observers.length] = callback;

        if (!this.connected) {
            webChannel.exec({
                type: QWebChannelMessageTypes.connectToSignal,
                object: sender.__id__,
                signal: signalIndex
            });
            this.connected = true;
        }
    };

    this.disconnect = function(callback)
    {
        if (typeof callback !== "function") {
            console.error("Bad callback given to disconnect from signal " + sender.__id__ + "::" + signalIndex);
            return;
        }

        for (var i = 0; i < this.observers.length; i++) {
            if (this.observers[i] === callback) {
                this.observers.splice(i, 1);
                break;
            }
        }

        if (this.observers.length === 0 && this.connected) {
            webChannel.exec({
                type: QWebChannelMessageTypes.disconnectFromSignal,
                object: sender.__id__,
                signal: signalIndex
            });
            this.connected = false;
        }
    };

    this.fire = function(args)
    {
        for (var i = 0; i < this.observers.length; i++) {
            var callback = this.observers[i];
            callback.apply(callback, args);
        }
    };

    this.connected = false;
    this.observers = [];
}
