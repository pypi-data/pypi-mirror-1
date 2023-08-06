kukit.actionsGlobalRegistry.register("menuSlideRight", function(oper) {
    oper.evaluateParameters(["speed","node"], {}, "menuSlideRight action");
    $(oper.parms.node).animate({left:"190px"},oper.parms.speed);
});


kukit.actionsGlobalRegistry.register("menuSlideLeft", function(oper) {
    oper.evaluateParameters(["speed","node"], {}, "menuSlideLeft action");
    $(oper.parms.node).animate({left:"0px"},oper.parms.speed);
});

kukit.actionsGlobalRegistry.register("menuSlideToggle", function(oper) {
    oper.evaluateParameters(["speed","node"], {}, "menuSlideToggle action");
    $("#"+oper.parms.node).slideToggle(oper.parms.speed);
});

kukit.actionsGlobalRegistry.register("menuToggleContent", function(oper) {
    oper.evaluateParameters(["node", "content_class"], {}, "menuToggleContent action");
    $("."+oper.parms.node).toggleClass(oper.parms.content_class);
});
