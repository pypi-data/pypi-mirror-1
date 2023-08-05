
new function () {
kukit.actionsGlobalRegistry.register('resetScrollbar', function (oper) {
;;; oper.componentName = '[resetScrollbar] action';
    
	var node = oper.node;
	node.scrollTop = node.scrollHeight
});
kukit.commandsGlobalRegistry.registerFromAction(
    'resetScrollbar', kukit.cr.makeSelectorCommand);
}();
