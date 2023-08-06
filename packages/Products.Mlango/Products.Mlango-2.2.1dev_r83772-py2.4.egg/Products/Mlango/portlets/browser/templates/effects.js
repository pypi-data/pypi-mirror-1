/**
 * Mlango effects for even more fun...
 */

kukit.actionsGlobalRegistry.register("menuSlideRight", function(oper) {
    oper.evaluateParameters(["speed","node"], {}, "menuSlideRight action");
    jq(oper.parms.node).animate({left:"180px"},oper.parms.speed);
});


kukit.actionsGlobalRegistry.register("menuSlideLeft", function(oper) {
    oper.evaluateParameters(["speed","node"], {}, "menuSlideLeft action");
    jq(oper.parms.node).animate({left:"0px"},oper.parms.speed);
});

kukit.actionsGlobalRegistry.register("menuSlideToggle", function(oper) {
    oper.evaluateParameters(["speed","node"], {}, "menuSlideToggle action");
    jq("#"+oper.parms.node).slideToggle(oper.parms.speed);
});

kukit.actionsGlobalRegistry.register("menuToggleContent", function(oper) {
    oper.evaluateParameters(["node", "content_class"], {}, "menuToggleContent action");
    jq("#"+oper.parms.node).toggleClass(oper.parms.content_class);
});
