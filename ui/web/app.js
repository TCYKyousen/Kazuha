document.addEventListener("DOMContentLoaded", function() {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const pageId = item.getAttribute('data-page');
            
            // Update nav active state
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Show page
            pages.forEach(p => p.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
        });
    });

    // QWebChannel Setup
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.bridge = channel.objects.Bridge;
        const bridge = window.bridge;

        // Helper to bind properties
        function bind(propName, elemId, type = 'value') {
            const elem = document.getElementById(elemId);
            if (!elem) return;

            // Initial value
            if (type === 'checkbox') {
                elem.checked = bridge[propName];
            } else if (type === 'text') {
                elem.innerText = bridge[propName];
            } else {
                elem.value = bridge[propName];
            }

            // Listen for changes from Python
            const signalName = propName + 'Changed';
            if (bridge[signalName]) {
                bridge[signalName].connect(function() {
                    console.log('Signal received: ' + signalName);
                    // Re-read property because signal arguments might vary or be empty
                    // Accessing the property again ensures we get the latest value from cache/backend
                    if (type === 'checkbox') {
                        elem.checked = bridge[propName];
                    } else if (type === 'text') {
                        elem.innerText = bridge[propName];
                    } else {
                        elem.value = bridge[propName];
                    }
                });
            }

            // Listen for user interactions
            elem.addEventListener('change', function() {
                let val;
                if (type === 'checkbox') {
                    val = elem.checked;
                } else if (type === 'select') {
                    val = parseInt(elem.value); // Convert to int for indices
                } else {
                    val = elem.value;
                }
                bridge[propName] = val;
            });
        }

        // Bindings
        bind('enableStartUp', 'enableStartUp', 'checkbox');
        bind('enableSystemNotification', 'enableSystemNotification', 'checkbox');
        bind('checkUpdateOnStart', 'checkUpdateOnStart', 'checkbox');

        bind('themeModeIndex', 'themeModeIndex', 'select');
        bind('screenPaddingIndex', 'screenPaddingIndex', 'select');

        bind('timerPositionIndex', 'timerPositionIndex', 'select');
        bind('navPositionIndex', 'navPositionIndex', 'select');
        
        bind('enableClock', 'enableClock', 'checkbox');
        bind('clockPositionIndex', 'clockPositionIndex', 'select');
        bind('clockShowSeconds', 'clockShowSeconds', 'checkbox');
        bind('clockShowDate', 'clockShowDate', 'checkbox');
        bind('clockFontWeightIndex', 'clockFontWeightIndex', 'select');

        // Update Info
        bind('updateStatusTitle', 'updateStatusTitle', 'text');
        bind('updateLastCheckText', 'updateLastCheckText', 'text');
        bind('updateLogs', 'updateLogs', 'text');
        bind('versionText', 'versionText', 'text');

        // Actions
        document.getElementById('btnCheckUpdate').addEventListener('click', function() {
            bridge.checkUpdate();
        });

        // Theme handling in JS (apply to body)
        function updateTheme() {
            const mode = bridge.themeModeIndex; // 0: Light, 1: Dark, 2: Auto
            // We can just use the index or the string value if mapped. 
            // In python: ["Light", "Dark", "Auto"]
            // Here we just toggle a class or attribute on body
            if (mode === 1) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else if (mode === 0) {
                document.documentElement.setAttribute('data-theme', 'light');
            } else {
                // Auto - simplistic check
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                    document.documentElement.setAttribute('data-theme', 'dark');
                } else {
                    document.documentElement.setAttribute('data-theme', 'light');
                }
            }
        }

        // Initial theme
        updateTheme();
        
        // Listen to theme change
        bridge.themeModeIndexChanged.connect(updateTheme);
    });
});
