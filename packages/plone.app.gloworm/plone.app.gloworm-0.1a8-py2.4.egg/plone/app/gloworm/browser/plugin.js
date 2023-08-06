kukit.actionsGlobalRegistry.register("resizePanel", function(oper) {
    /* Resize the GloWorm panel to fit its contents.
       TODO: Right now, the extral 35 pixels are completely arbitrary, figure out a better value.
    */
    newHeight = document.getElementById('glowormPanelBody').offsetHeight + 35;
    document.getElementById('glowormPanel').style.height = newHeight;
    document.getElementById('glowormPageWrapper').style.bottom = newHeight;
});
kukit.commandsGlobalRegistry.registerFromAction('resizePanel',
    kukit.cr.makeGlobalCommand);
    
kukit.actionsGlobalRegistry.register('scrollNavTree', function(oper) {
;;; oper.componentName = '[scrollNavTree] action';
;;; oper.evaluateParameters([], {});
    var itemNode = oper.node.parentNode;
    var itemScrollPos = itemNode.offsetTop;
    navTree = document.getElementById('glowormPanelNavTree')
    visibleTop = navTree.scrollTop;
    visibleBottom = visibleTop + navTree.offsetHeight;
    if (!((itemScrollPos > visibleTop-50) && (itemScrollPos < visibleBottom + 50))){
        document.getElementById('glowormPanelNavTree').scrollTop = itemScrollPos - parseInt(navTree.offsetHeight/2);
    }
});

kukit.commandsGlobalRegistry.registerFromAction('scrollNavTree', 
                                                kukit.cr.makeSelectorCommand);
                                                
var _ParseTALAttributes = function() {
    this.check = function(attrs, node){};
    this.eval = function(attrs, node) {
        attrs = kukit.dom.getRecursiveAttribute(node, 'tal:attributes', true, kukit.dom.getAttribute);
        // For some wierd reason, we're ending up with 3 functions in the attrs variable. Remove them by brute force.
        //alert(attrs);
        //attrs = attrs.slice(0, attrs.length - 3);
        //alert(attrs);
        splitAttrs = attrs.split(';');
        retArray = [];
        for(s in splitAttrs){
            line = splitAttrs[s];
            
            lineResult = [];
            result = kukit.dom.getRecursiveAttribute(node, line.split(' ')[0], true, kukit.dom.getAttribute);
            alert([line.split(' ')[0], line.split(' ')[1], result]);
            //line.push(retValue);
        }
        return retArray;
   };
};

kukit.pprovidersGlobalRegistry.register('parseTALAttributes', _ParseTALAttributes);

var _GetSourceAnnotation = function() {
  this.check = function(attrs, node){};
  this.eval = function(attrs, node) {
      siblingNode = node;
      parentalNode = node.parentNode;
      while(parentalNode){
          while(siblingNode){
              if ((siblingNode.nodeType == document.COMMENT_NODE) && (siblingNode.data.indexOf('====='))){
                  return siblingNode.data;
              }          
              siblingNode = siblingNode.previousSibling;
          }
          siblingNode = parentalNode;
          parentalNode = parentalNode.parentNode;
      }
      return '';
  };
};
kukit.pprovidersGlobalRegistry.register('sourceAnnotation', _GetSourceAnnotation);
