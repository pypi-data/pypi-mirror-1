if (typeof(kukit) != 'undefined') {
    kukit.actionsGlobalRegistry.register("explorer-updatecookies", function(oper) {
        oper.evaluateParameters(['portlethash'], {}, 'explorer-updatecookies action');
        var portlethash = oper.parms.portlethash;
        var nodes = cssQuery("#portletwrapper-"+portlethash+" li.navTreeFolderish");
        var uids = [];
        for (var i=0; i<nodes.length; i++) {
            var uid = nodes[i].className.match(/\bnode-(.+?)\b/)[1];
            var toggles = cssQuery("#portletwrapper-"+portlethash+" li.node-"+uid+" > span.expandedNode");
            if (toggles.length > 0) {
                if (!hasClassName(toggles[0], 'showChildren')) {
                    uids[uids.length] = uid;
                }
            };
        };
        var cookie = uids.join('|');
        console.log(cookie);
        createCookie('expanded-'+portlethash, cookie);
    });
    kukit.commandsGlobalRegistry.registerFromAction('explorer-updatecookies',
        kukit.cr.makeSelectorCommand);
    kukit.actionsGlobalRegistry.register("explorer-togglechilds", function(oper) {
        oper.evaluateParameters(['uid'], {}, 'explorer-togglechilds action');
        var uid = oper.parms.uid;
        var uls = cssQuery("li.node-"+uid+" > ul");
        if (uls.length > 0) {
            if (hasClassName(uls[0], 'hideChildren')) {
                removeClassName(uls[0], 'hideChildren');
            } else {
                addClassName(uls[0], 'hideChildren');
            };
        };
    });
    kukit.commandsGlobalRegistry.registerFromAction('explorer-togglechilds',
        kukit.cr.makeSelectorCommand);
};
