pollapli.test="truc";

pollapli.openNodeDialog=function (nodeId,mode)
{
    if(nodeId!=-1)
    {
        node=manager.environments[1].nodes[nodeId];
    }
    else
    {
        node="";
    }
   
    //alert("node:"+ node+" node name:"+node.name);
    $('#node-dialog').jqotesub('#nodes_dialog_tmpl', {'node':node,'mode':mode});  
    $("#node-dialog button").button();
    $('#node-dialog').dialog('open');
} 

pollapli.openNodeDialog_test=function (nodeId,mode)
{
    if(nodeId!=-1)
    {
        node=manager.nodes[nodeId];
    }
    else
    {
        node="";
    }
   
    //alert("node:"+ node+" node name:"+node.name);
    $('#node-dialog').jqotesub('#nodes_dialog_tmpl', {'node':node,'mode':mode});  
    $("#node-dialog button").button();
    $('#node-dialog').dialog('open');
} 



pollapli.validateNodeOp=function(op,id)
{
  
      
       
        
        var tmpnode=new Object();
        tmpnode.name=$("#nodes_dialog_name").val();
        tmpnode.description=$("#nodes_dialog_description").val();

 
        if (op=="create")
        {
          manager.addNodeTest(tmpnode);
        }
        else if (op=="modify")
        {
          
          
          manager.updateNodeTest(tmpnode,id);
        }
}


pollapli.update=function(op,id)
{
 
        var tmpnode=new Object();
        tmpnode.name=$("#nodes_dialog_name").val();
        tmpnode.description=$("#nodes_dialog_description").val();

        if (op=="create")
        {
          manager.create_node(tmpnode);
        }
        else if (op=="modify")
        {
          manager.update_node(tmpnode,id);
        }
}