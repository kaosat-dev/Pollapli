//  root Objectif ;
//  initialize constants, array
var jQXB = {
    version: "1.1.20110802",
    initialized: false,
    alertOnError: false,
    m: { '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', '\r': '\\r', '"': '\\"', '\\': '\\\\' },
    datasourcesCollectionOrigValues: new Array(),
    datasourcesCollection: new Array(),
    charset: 'charset=utf-8',
    onBeforeUpdateCallBacks: new Array(),
    onAfterUpdateCallBacks: new Array(),
    onBeforeDataSourceBindCallBacks: new Array(),
    onAfterDataSourceBindCallBacks: new Array(),
    onBeforeTemplateBindCallBacks: new Array(),
    onAfterTemplateBindCallBacks: new Array(),
    onTemplateItemBindedCallbacks: new Array(),
    messageSubscribers: new Array(),
    internalOnBinding: new Array(),
    JQXB_DEFAULT_CHANGE_EVENT: "change",
    JQXB_DATASOURCE_ATTR: "jqxb-datasource",
    JQXB_DATASOURCE_MEMBER_ATTR: "jqxb-datamember",
    JQXB_TEMPLATE_ATTR: "jqxb-template",
    JQXB_OCCURENCY_ATTR: "jqxb-occurency",
    // Template
    JQXB_TEMPLATECONTAINER_ATTR: "jqxb-templatecontainer",
    JQXB_TEMPLATEITEMPREFIX_ATTR: "jqxb-templateitemidprfx",
    JQXB_TEMPLATEOWNER_ATTR: "jqxb-itemtemplate",
    JQXB_TEMPLATEITEMDATAMEMBER_ATTR: "jqxb-itemdatamember",
    // JQXB_TEMPLATEITEM: "jqxb-templateitem",
    JQXB_TEMPLATEITEMDATASOURCE_ATTR: "jqxb-itemdatasource",
    JQXB_TEMPLATEITEMIDX_ATTR: "jqxb-itemdatasourceidx",
    JQXB_CHANGEONEVENT_ATTR: "jqxb-changeonevent",
    JQXB_BINDEDATTRIBUTE_ATTR: "jqxb-bindedattribute",
    // combo & datalist specific attribute
    JQXB_LISTSOURCE: "jqxb-listsource",
    JQXB_LISTVALUE: "jqxb-listvalue",
    JQXB_LISTTEXT: "jqxb-listtext"
}

/**************************
*   jSON Serializer
*******************************/
jQXB.toJSON = function (value, whitelist) {
    var a,          // The array holding the partial texts.
        i,          // The loop counter.
        k,          // The member key.
        l,          // Length.
        r = /["\\\x00-\x1f\x7f-\x9f]/g,
        v;          // The member value.

    switch (typeof value) {
        case 'string':
            return r.test(value) ?
            '"' + value.replace(r, function (a) {
                var c = jQXB.m[a];
                if (c) { return c; }
                c = a.charCodeAt();
                return '\\u00' + Math.floor(c / 16).toString(16) + (c % 16).toString(16);
            }) + '"' :
            '"' + value + '"';

        case 'number':
            return isFinite(value) ? String(value) : 'null';

        case 'boolean':
        case 'null':
            return String(value);

        case 'object':
            if (!value) {
                return 'null';
            }
            if (typeof value.toJSON === 'function') {
                return jQXB.toJSON(value.toJSON());
            }
            a = [];
            if (typeof value.length === 'number' &&
                !(value.propertyIsEnumerable('length'))) {
                l = value.length;
                for (i = 0; i < l; i += 1) {
                    a.push(jQXB.toJSON(value[i], whitelist) || 'null');
                }
                return '[' + a.join(',') + ']';
            }
            if (whitelist) {
                l = whitelist.length;
                for (i = 0; i < l; i += 1) {
                    k = whitelist[i];
                    if (typeof k === 'string') {
                        v = jQXB.toJSON(value[k], whitelist);
                        if (v) {
                            a.push(jQXB.toJSON(k) + ':' + v);
                        }
                    }
                }
            } else {
                for (k in value) {
                    if (typeof k === 'string') {
                        v = jQXB.toJSON(value[k], whitelist);
                        if (v) {
                            a.push(jQXB.toJSON(k) + ':' + v);
                        }
                    }
                }
            }
            return '{' + a.join(',') + '}';
    }
};

/************************************************
*    Initialization
************************************************/

// initialize object
// Verify the JQXB attributes correctness depending on
// [verify] flag
// [balertOnError]
jQXB.initialize = function (verify, balertOnError) {
    // verify datasource for simple binding
    var verifyErrors = new Array();
    if (verifyErrors) {
        jQuery('[' + jQXB.JQXB_DATASOURCE_ATTR + ']:not([' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '])').each(function () {
            if (jQuery(this).attr(jQXB.JQXB_DATASOURCE_MEMBER_ATTR) == undefined)
                verifyErrors.push(jQuery(this).attr(jQXB.JQXB_DATASOURCE_ATTR) + " missing " + jQXB.JQXB_DATASOURCE_MEMBER_ATTR + "attribute");
        });
    }
    if (jQXB.alertOnError != undefined)
        jQXB.alertOnError = balertOnError;
    // Attach Event Handlers
    if (jQXB.initialized)
        return jQXB;
    jQXB.initialized = true;
    return jQXB.attachChangeEvents();
}

/*****************************************
*  Misc
****************************************/
// Reload data from underlying object 
// params: datasourceName
jQXB.refreshControls = function (datasourceName, occurrency, datamemberName) {
    var selector;
    if (occurrency == undefined) {
        if (datamemberName == undefined)
            selector = '[' + jQXB.JQXB_DATASOURCE_ATTR + "=" + datasourceName + '][' + jQXB.JQXB_DATASOURCE_MEMBER_ATTR + ']';
        else
            selector = '[' + jQXB.JQXB_DATASOURCE_ATTR + "=" + datasourceName + '][' + jQXB.JQXB_DATASOURCE_MEMBER_ATTR + "=" + datamemberName + ']';
    }
    else {
        if (datamemberName == undefined) {
            selector = '[' + jQXB.JQXB_DATASOURCE_ATTR + "=" + datasourceName + '][' + 
                             jQXB.JQXB_TEMPLATECONTAINER_ATTR + '] [' +
                             jQXB.JQXB_TEMPLATEOWNER_ATTR + '][' + 
                             jQXB.JQXB_TEMPLATEITEMIDX_ATTR + '=' + occurrency +'] [' +
                             jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR + ']';
        }
        else {
            selector = '[' + jQXB.JQXB_DATASOURCE_ATTR + "=" + datasourceName + '][' +
                             jQXB.JQXB_TEMPLATECONTAINER_ATTR + '] [' +
                             jQXB.JQXB_TEMPLATEOWNER_ATTR + '][' +
                             jQXB.JQXB_TEMPLATEITEMIDX_ATTR + '=' + occurrency +'] [' +
                             jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR + "=" + datamemberName + ']';
            
        }
    }
    jQuery(selector).each(function () {
        jQXB.getmemberValue(jQXB.getDataSource(datasourceName), occurrency, jQuery(this).attr(jQXB.JQXB_DATASOURCE_MEMBER_ATTR) || jQuery(this).attr(jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR), jQuery(this));
    });
    return jQXB;
}

// Attach events for present and future element
jQXB.attachChangeEvents = function () {
    // Attach event for simple databinding
    jQuery("body").delegate('[' + jQXB.JQXB_DATASOURCE_MEMBER_ATTR + '][' + jQXB.JQXB_DATASOURCE_ATTR + ']', jQXB.JQXB_DEFAULT_CHANGE_EVENT, function () {
        var jQryElem = jQuery(this);
        var attribute = jQryElem.attr('jqxb-bindedattribute');
        var value;
        if (attribute == undefined)
            value = jQuery(this).val();
        else
            value = jQuery(this).attr(attribute);
        jQXB.setmemberVarvalue(jQryElem.attr(jQXB.JQXB_DATASOURCE_ATTR), null, jQryElem.attr(jQXB.JQXB_DATASOURCE_MEMBER_ATTR), value, jQryElem);
    });
    // Attach event for Template databinding
    jQuery("body").delegate('[' + jQXB.JQXB_DATASOURCE_ATTR + '][' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '] [' + jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR + ']', jQXB.JQXB_DEFAULT_CHANGE_EVENT, function () {
        var jQryElem = jQuery(this);
        var templateName = jQryElem.parents('[' + jQXB.JQXB_TEMPLATEITEMIDX_ATTR + ']').first().attr(jQXB.JQXB_TEMPLATEOWNER_ATTR);
        var occurrency = jQryElem.parents('[' + jQXB.JQXB_TEMPLATEITEMIDX_ATTR + ']').first().attr(jQXB.JQXB_TEMPLATEITEMIDX_ATTR);
        var attribute = jQryElem.attr('jqxb-bindedattribute');
        var value;
        if (attribute == undefined)
            value = jQuery(this).val();
        else
            value = jQuery(this).attr(attribute);
        jQXB.setmemberVarvalue(jQryElem.parents('[' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '=' + templateName + ']').attr(jQXB.JQXB_DATASOURCE_ATTR), occurrency, jQryElem.attr(jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR), value, jQryElem);
    });
    return jQXB;
}

// Bind a single HTML element the coresponding event to update the underlying object stored in the binding variable
// jQXB.JQXB_CHANGEONEVENT_ATTR contains the default event to be hooked 
// the attribute  JQXB_CHANGEONEVENT_ATTR: "jqxb-changeonevent" can be use to specified alternative event
// 
jQXB.attachChangeEvent = function (datasourceName, occurrency, internalVarmember, jQryCtl) {
    var hookevent = jQryCtl.attr(jQXB.JQXB_CHANGEONEVENT_ATTR);
    if (hookevent == undefined)
        hookevent = jQXB.JQXB_DEFAULT_CHANGE_EVENT;
    // prevent event fire twice after rebinding
    jQryCtl.unbind(hookevent, function () {
        jQXB.setmemberVarvalue(datasourceName, occurrency, internalVarmember, jQXB.getValueFromAttrib(jQuery(this)), jQuery(this));
    });
    jQryCtl.bind(hookevent, function () {
        jQXB.setmemberVarvalue(datasourceName, occurrency, internalVarmember, jQXB.getValueFromAttrib(jQuery(this)), jQuery(this));
    });
    return jQXB;
}


/**********************************************
*  Event Handlers subscriptions
***********************************************/
//
jQXB.addOnTemplateItemBoundhnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnTemplateItemBoundhnd Error: handler must be a function");
    jQXB.onTemplateItemBindedCallbacks.push(handler);
    return jQXB;
}
jQXB.delOnTemplateItemBoundhnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnTemplateItemBoundhnd Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onTemplateItemBindedCallbacks,handler);
    return jQXB;
}

// Register a call back to be invoked before updating 
jQXB.addOnBeforeUpdatehnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnBeforeUpdatehnd   Error: handler must be a function");
    jQXB.onBeforeUpdateCallBacks.push(handler);
    return jQXB;
}
jQXB.delOnBeforeUpdatehnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnBeforeUpdatehnd Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onBeforeUpdateCallBacks,handler);
    return jQXB;
}

// Register a call back function to handle the AfterUpdate of a member 
jQXB.addOnAfterUpdatehnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnAfterUpdatehnd   Error: handler must be a function");
    jQXB.onAfterUpdateCallBacks.push(handler);
    return jQXB;
}
jQXB.delOnAfterUpdatehnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnAfterUpdatehnd Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onAfterUpdateCallBacks,handler);
    return jQXB;
}

// Adding Removing OnBeforeDataSourceBind event handlers
jQXB.addOnBeforeDataSourceBindhnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnBeforeDataSourceBindhnd Error: handler must be a function");
    jQXB.onBeforeDataSourceBindCallBacks.push(handler);
    return jQXB;
}
jQXB.delOnBeforeDataSourceBindhnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnBeforeDataSourceBindhnd  Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onBeforeDataSourceBindCallBacks,handler);
    return jQXB;
}

// Adding Removing  OnAfterDataSource event handler
jQXB.addOnAfterDataSourceBindhnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnAfterDataSourceBindhnd Error: handler must be a function");
    jQXB.onAfterDataSourceBindCallBacks.push(handler);
    return jQXB;
}
jQXB.delOnAfterDataSourceBindhnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnAfterDataSourceBindhnd  Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onAfterDataSourceBindCallBacks,handler);
    return jQXB;
}
// Adding Removing  OnBeforeTemplateBind event handlers
jQXB.addOnBeforeTemplateBindhnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnAfterTemplateBindhnd  Error: handler must be a function");
    jQXB.onBeforeTemplateBindCallBacks.push(handler);
    return jQXB;
}
jQXB.delOnBeforeTemplateBindhnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnBeforeTemplateBindhnd  Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onBeforeTemplateBindCallBacks,handler);
    return jQXB;
}

// Adding  removing OnAfterTemplateBind Event Handler
jQXB.addOnAfterTemplateBindhnd = function (handler) {
	if(typeof(handler) != 'function')
		alert("jQXB.addOnAfterTemplateBindhnd  Error: handler must be a function");
    jQXB.onAfterTemplateBindCallBacks.push(handler);
    return jQXB;
}
jQXB.delOnAfterTemplateBindhnd = function(handler){
	if(typeof(handler) != 'function')
		alert("jQXB.delOnAfterTemplateBindhnd  Error: handler must be a function");
    jQXB.delOnEventhdn(jQXB.onAfterTemplateBindCallBacks,handler);
    return jQXB;
}

jQXB.delOnEventhdn = function(handlersArray,handler){
	if(typeof(handler) != 'function'){
		alert('jQXB.delOnEventhdn Error: handler param must be a function');
		return;
	}
	for(idx = 0; idx < handlersArray.length; idx++)
	{
		if(handlersArray[idx].toString() == handler.toString())
		    handlersArray.splice(idx, 1);
	}
}

/*********************************************************
*  DataSource operations
**********************************************************/

// store a variable into a binder variable
// param:   datasourceName = the name to assign to the specific datasource
// param:   the object or array objects to be stored
jQXB.setDataSource = function (datasourceName, object, autorefhesh) {
    var datasource = jQXB.datasourcesCollection[datasourceName];
    if (datasource == undefined)
        datasource = { datasource: object, autorefresh: autorefhesh };
    else
        datasource.datasource = object;
    if (autorefhesh != undefined)
        datasource.autorefresh = autorefhesh;
    jQXB.datasourcesCollection[datasourceName] = datasource;
    jQXB.datasourcesCollectionOrigValues[datasourceName] = object;
    return jQXB;
}


// return the underlying object stored in a binder variable
jQXB.getDataSource = function getDataSource(datasourceName){
    try {
        return jQXB.datasourcesCollection[datasourceName].datasource;
    }
    catch (e) {
        e.arguments = arguments;
        alert(jQXB.diags.dumpobj(e, "[ERROR]", "->"));
    }
}
jQXB.getDataSourceContainer = function (datasourceName) {
    return jQXB.datasourcesCollection[datasourceName];
}

// return the underlying object stored in a binder variable
jQXB.getDataSourceOrigValue = function (datasourceName) {
    return jQXB.datasourcesCollectionOrigValues[datasourceName];
}

// add or insert an object to the underlying binder variable and refresh video for any template associated
// param:   datasourceName      = the name of the binder variable
// param:   Object          = the new object instance to add
//param:    atIdx	         = where to insert ne object , if no specified the object will be appended
jQXB.addRowToDataSource = function (datasourceName, Object, atIdx) {
    if (!jQXB.utils.isEnumerable(jQXB.getDataSource(datasourceName))) {
        alert(datasourceName + "  must be enumerable in order to add object ");
        return;
    }
    if (atIdx == undefined)
        jQXB.getDataSource(datasourceName).push(Object);
    else
        jQXB.getDataSource(datasourceName).splice(atIdx, 0, Object);
    jQXB.bindTemplate(datasourceName);
    return jQXB;
}

// add an object to the underlying binder variable and refresh video for any template associated
// param:   datasourceName      = the name of the binder variable
// param:   Object          = the new object instance to add
// *****  DEPRECATED ********
jQXB.addObjectToDataSource = function (datasourceName, Object) {
    return jQXB.addRowToDataSource(datasourceName,Object);
}

// delete a element from the underlying binder and refresh video for any template binded 
// param: datasourceName        = the name of the binder
// param: Occurency         = rapresent the n-element stored in the binder variable
jQXB.deleteRowFromDataSource = function(datasourceName,Occurrency){
    if (!jQXB.utils.isEnumerable(jQXB.getDataSource(datasourceName))) {
        alert(datasourceName + "  must be enumerable in order to remove object ");
        return;
    }
    jQXB.getDataSource(datasourceName).splice(Occurrency, 1);
    jQuery('[' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '][' + jQXB.JQXB_DATASOURCE_ATTR + '=' + datasourceName + '] > [' + jQXB.JQXB_TEMPLATE_ATTR + '][' + jQXB.JQXB_TEMPLATEITEMPREFIX_ATTR + ']').each(function () {
        jQXB.deleteTemplateRow(jQuery(this).attr(jQXB.JQXB_TEMPLATE_ATTR), Occurrency);
    });
    return jQXB;

}

// delete a element from the underlying binder and refresh video for any template binded 
// param: datasourceName        = the name of the binder
// param: Occurency         = rapresent the n-element stored in the binder variable
// *****  DEPRECATED ********
jQXB.deleteObjectFromDataSource = function (datasourceName, Occurrency) {
	return jQXB.deleteRowFromDataSource(datasourceName,Occurrency);
}

/*******************************************************
* Remote CRUD Operations - jQuery delegations
********************************************************/

// A shortcut to a postJSON call to execute a POST onto a server
// param:   url      =  the url 
// param:   data     = the javascript object to post or delere
// param:   [successCallBack] = function to invoke after a succesfully call
// param:   [failureCallBack] = function to invoke after a unsuccesfully call
jQXB.saveJSON = function (url, data, successCallBack, failureCallBack) {
    return jQXB.postJSON(url, "post", data, successCallBack, failureCallBack);
}

// A shortcut to a postJSON call to execute a DELETE onto a server
// param:   url      =  the url 
// param:   data     = the javascript object to post or delere
// param:   [successCallBack] = function to invoke after a succesfully call
// param:   [failureCallBack] = function to invoke after a unsuccesfully call
jQXB.deleteJSON = function (url, data, successCallBack, failureCallBack) {
    return jQXB.postJSON(url, "delete", data, successCallBack, failureCallBack);
}

// Execute a POST jQuery.ajax
// param:   url      =  the url 
// param:   method   = method to use
// param:   data     = the javascript object to post or delere
// param:   [successCallBack] = function to invoke after a succesfully call
// param:   [failureCallBack] = function to invoke after a unsuccesfully call
jQXB.postJSON = function (url, method, data, successCallBack, failureCallBack) {
    return jQXB.ajaxCall(url, method, data, successCallBack, failureCallBack);
}

// Delegate ajax call to jQuery.ajax
jQXB.ajaxCall = function (url, method, data, successCallBack, failureCallBack) {
    jQuery.ajax({
        type: method,
        traditional: true,
        url: url,
        async: false,
        data: jQXB.toJSON(data),
        dataType: "json",
        contentType: 'application/json; ' + jQXB.charset,
        success: function (data) {
            if (successCallBack != undefined)
                successCallBack(data);
        },
        error: function (data) {
            if (failureCallBack != undefined) {
                if (jQXB.alertOnError)
                    alert('jQXB.ajaxCall ERROR: url:' + url + ' method: ' + method);
                failureCallBack(data);
            }
        }
    });
    return jQXB;
}

// Get a Json data from remote server
jQXB.getJSON = function (url, data, successCallBack, failureCallBack) {

    jQuery.ajax({
        type: 'get',
        traditional: true,
        url: url,
        async: false,
        data: data,
        dataType: "json",
        contentType: 'application/json; ' + jQXB.charset,
        success: function (data) {
            if (successCallBack != undefined)
                successCallBack(data);
        },
        error: function (data) {
            if (failureCallBack != undefined) {
                if (jQXB.alertOnError)
                    alert('jQXB.getJSON ERROR:');
                failureCallBack(data);
            }
        }
    });
    return jQXB;
}

/*********************************************************
*  Template handling functions
**********************************************************/

// delete a specific row of a template istantiated on client 
// param: templateName      = the name of the template
// param: Occurency         = the n-item template
jQXB.deleteTemplateRow = function (templateName, Occurrency) {
    var datasourceName, prfx, i, jQueryTplItemToDel;
    datasourceName = jQuery('[' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '=' + templateName + ']').first().attr(jQXB.JQXB_DATASOURCE_ATTR);
    jQuery('[' + jQXB.JQXB_TEMPLATEOWNER_ATTR + '=' + templateName + '][' + jQXB.JQXB_TEMPLATEITEMIDX_ATTR + '=' + Occurrency + ']').remove();
    prfx = jQuery('[' + jQXB.JQXB_TEMPLATE_ATTR + '=' + templateName + '][' + jQXB.JQXB_TEMPLATEITEMPREFIX_ATTR + ']').first().attr(jQXB.JQXB_TEMPLATEITEMPREFIX_ATTR);
    i = 0;
    // Renumber Templates Instance occurency
    jQuery('[' + jQXB.JQXB_TEMPLATEOWNER_ATTR + '=' + templateName + '][' + jQXB.JQXB_TEMPLATEITEMIDX_ATTR + ']').each(function () {
        jQuery(this).attr('id', prfx + "_" + i).attr(jQXB.JQXB_TEMPLATEITEMIDX_ATTR, i);
        jQXB.bindElementsTemplates(datasourceName, jQuery(this).attr(jQXB.JQXB_TEMPLATEOWNER_ATTR), i, jQuery(this));
        i++;
    });
    return jQXB;
}

// Clear all the templates instantiated for a specific template
// param: templateName      = template name
jQXB.clearTemplateInstances = function (templateName) {
    jQuery('[' + jQXB.JQXB_TEMPLATEOWNER_ATTR + '=' + templateName + ']').unbind().remove();
    return jQXB;
}

/***********************************************************
*  Binding functions
***********************************************************/

// Execute a global binding for all HTML elements and template associated to a specifica binder variable
// param: datasourceName = the name of the datasource, if not specified jQXB bind all configured dataSource
// param: [contextScope] = actually not used
// 
jQXB.doBind = function (datasourceName, contextScope) {
    // Template Binding
	var datasourceNames = new Array();
	if(datasourceName != undefined)
	   datasourceNames.push(datasourceName);
	else
	{
		for(var name in jQXB.datasourcesCollection)
		{
			datasourceNames.push(name);
		}
	}
	//var datasourceArrays = (datasourceName == undefined) ? 
	//	jQXB.datasourcesCollection.slice(0):jQXB.datasourcesCollection.slice(jQXB.datasourcesCollection.indexOf(datasourceName),1);
	try {
	    for (var idx = 0; idx < datasourceNames.length; idx++) {
	            jQXB.bindList(datasourceNames[idx], contextScope);
				jQXB.bindSingleDataMember(datasourceNames[idx], contextScope);
				jQXB.bindTemplate(datasourceNames[idx], contextScope);

			}
	}
	catch (e) {
		e.arguments = arguments;
		alert(jQXB.diags.dumpobj(e,"ERROR","->"));
	}

    return jQXB;
}

// Bind each list element
jQXB.bindList = function (dataSourceName, contextscope) {
    jQuery('[' + jQXB.JQXB_LISTSOURCE + '=' + dataSourceName + '][' + jQXB.JQXB_LISTVALUE + '][' + jQXB.JQXB_LISTVALUE + ']').each(
		function () { jQXB.utils.filllist(jQuery(this), jQXB.getDataSource(dataSourceName), jQuery(this).attr(jQXB.JQXB_LISTVALUE), jQuery(this).attr(jQXB.JQXB_LISTTEXT)) }
	);
}

// Set a simple binding for each element
// param: datasourceName = the name of the datasource
// param: [contextScope] = actually not used 
jQXB.bindSingleDataMember = function (datasourceName, contextScope) {
    // Simple Binding
    for (var i = 0; i < jQXB.onBeforeDataSourceBindCallBacks.length; i++) {
        jQXB.onBeforeDataSourceBindCallBacks[i](datasourceName, jQXB.getDataSource(datasourceName));
    }
    jQuery('[' + jQXB.JQXB_DATASOURCE_ATTR + '=' + datasourceName + ']:not([' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '])', contextScope).each(function () {
        jQXB.bindElement(datasourceName, null, jQuery(this).attr(jQXB.JQXB_DATASOURCE_MEMBER_ATTR), jQuery(this));
    });
    for (var i = 0; i < jQXB.onAfterDataSourceBindCallBacks.length; i++) {
        jQXB.onAfterDataSourceBindCallBacks[i](datasourceName, jQXB.getDataSource(datasourceName));
    }
    return jQXB;
}

// Set the correct event to intercept value change
// Retrieve the current value from internalVar
// param: datasourceName = the name or the datasource stored in internal variables
// param: occurrency = the n element (rows) of the datasource. "undefined" if datatasource containes a single object
// param: datamemberName = the name to the member to bind
// param: jQryElementInstance = the jQuery object to bind
jQXB.bindElement = function (datasourceName, occurrency, dataMemberName, jQryElementInstance) {
    var internalData = jQXB.getDataSource(datasourceName);
    //jQXB.attachChangeEvent(datasourceName, occurrency, dataMemberName, jQryElementInstance);
    jQXB.getmemberValue(internalData, occurrency, dataMemberName, jQryElementInstance);
    return jQXB;
}

// Configure a binded template
// Inspect all templates binded to a specific binder to proceed with binding
// param:   datasourceName      = the symbolic name of the binder object
// param:   contextScope    = actually nont used"
jQXB.bindTemplate = function (datasourceName, contextScope) {

    jQuery('[' + jQXB.JQXB_TEMPLATECONTAINER_ATTR + '][' + jQXB.JQXB_DATASOURCE_ATTR + '=' + datasourceName + ']').each(function () {

        var templateData, jQryTemplateContainer, currentTemplateName;
        templateData = jQXB.getDataSource(datasourceName);
        jQryTemplateContainer = jQuery(this);
        currentTemplateName = jQryTemplateContainer.attr(jQXB.JQXB_TEMPLATECONTAINER_ATTR);
        // Invoke callbacks
        for (var i = 0; i < jQXB.onBeforeTemplateBindCallBacks.length; i++) {
            jQXB.onBeforeTemplateBindCallBacks[i](datasourceName, jQXB.getDataSource(datasourceName), currentTemplateName);
        }
        // First STEP - 
        //First Bind Existen
        for (var i = 0; i < templateData.length; i++) {
            jQrySingleItem = jQuery(this).find('[' + jQXB.JQXB_TEMPLATEOWNER_ATTR + '][' + jQXB.JQXB_TEMPLATEITEMIDX_ATTR + '=' + i + ']');
            if (jQrySingleItem.length != 0) {
                // Row Already Existing
                jQuery(this).find('[' + jQXB.JQXB_TEMPLATEOWNER_ATTR + '][' + jQXB.JQXB_TEMPLATEITEMIDX_ATTR + '=' + i + ']').each(function () {
                    jQXB.bindElementsTemplates(datasourceName, currentTemplateName, i, jQuery(this));
                });
            }
            else {
                // New Row
                jQrySingleItem = jQryTemplateContainer.find('[' + jQXB.JQXB_TEMPLATE_ATTR + '=' + currentTemplateName + ']').clone();
                // jQryNewItem.removeAttr('jqxb-template');
                id = jQrySingleItem.attr(jQXB.JQXB_TEMPLATEITEMPREFIX_ATTR);
                id += "_" + i;
                jQrySingleItem.attr('id', id).
                        removeAttr(jQXB.JQXB_TEMPLATEITEMPREFIX_ATTR).
                        removeAttr(jQXB.JQXB_TEMPLATE_ATTR).
                        attr(jQXB.JQXB_TEMPLATEITEMIDX_ATTR, i).
                        attr(jQXB.JQXB_TEMPLATEOWNER_ATTR, currentTemplateName).
                        show().
                        appendTo(jQryTemplateContainer);
                jQXB.bindElementsTemplates(datasourceName, currentTemplateName, i, jQrySingleItem);
            }
            // invoke callbacks
            //for(i = 0;i < jQXB.onAfterTemplateBindCallBacks.length ; i++)
            // {
            //     jQXB.onAfterTemplateBindCallBacks[i](datasourceName,jQXB.getDataSource(datasourceName),currentTemplateName);
            // }
        }
    });
    return jQXB;
}

// Bind all HTML elements contained into the Template Item instance to data
// param: datasourceName            = symbolic Name of the binder object
// param: templateName          = the Name of the template containing the HTML controls involved in the binding process
// param: Occurency             = the n-template-element
// param: jQueryItemTemplate    = a jQuery object rapresenting the whole Item Template
jQXB.bindElementsTemplates = function (datasourceName, templateName, Occurency, jQueryItemTemplate) {
    jQueryItemTemplate.find('[' + jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR + ']').each(function () {
        var templateItemDatamemberName = jQuery(this).attr(jQXB.JQXB_TEMPLATEITEMDATAMEMBER_ATTR);
        jQXB.bindElement(datasourceName, Occurency, templateItemDatamemberName, jQuery(this));
    });
    // iterate for each callback function
    for (var idxcallBack = 0; idxcallBack < jQXB.onTemplateItemBindedCallbacks.length; idxcallBack++) {
        jQXB.onTemplateItemBindedCallbacks[idxcallBack](datasourceName, templateName, Occurency, jQXB.getDataSource(datasourceName)[Occurency], jQueryItemTemplate);
    }
    return jQXB;
}

/************************************************************
* Members value assignements functions 
************************************************************/
// Set a binder member value
// param:   datasourceName          = the symbolic name of the binder element
// param:   occurency           = rapresent the n-element contained in the binder object
// param:   internalVarMember   = name od the member to be setted
jQXB.setmemberVarvalue = function (datasourceName, occurrency, internalVarmember, value, jQryElement) {
    var memberpath, Member, dataSource;
    memberpath = internalVarmember.split(".");
    // retrieve the instance of the object contained in the binding variable
    dataSource = jQXB.getDataSource(datasourceName);
    if (dataSource === undefined && jQXB.alertOnError)
        alert('jQXB.setmemberVarvalue ERROR: no datasource \'' + datasourceName + '\' found. called from ' + jQXB.setmemberVarvalue.caller.toString());
    Member = jQXB.getMemberByReflection(dataSource, occurrency, memberpath);
    if (typeof (Member) == 'function')
        return;
	var arrLastItem = jQXB.onBeforeUpdateCallBacks.length;
    for (var i = 0; i < arrLastItem ; i++) {
        var bCancel = jQXB.onBeforeUpdateCallBacks[i](datasourceName, occurrency, Member, internalVarmember, value);
        if (bCancel == true) {
            // reset the underlying value
            jQXB.getmemberValue(dataSource, occurrency, internalVarmember, jQryElement);
            return;
        }
    }
    jQXB.setMemberValByReflection(dataSource, occurrency, memberpath, value);
    if (jQXB.getDataSourceContainer(datasourceName).autorefresh)
        jQXB.refreshControls(datasourceName, occurrency, internalVarmember);
	var arrLength = jQXB.onAfterUpdateCallBacks.length;
    for (var i = 0; i < arrLength; i++) {
        var bCancel = jQXB.onAfterUpdateCallBacks[i](datasourceName, occurrency,jQXB.getMemberByReflection(dataSource, occurrency, memberpath), internalVarmember, value);
    }
    return jQXB;
    //jQXB.doBind(datasourceName);
}

// Reflection setter
jQXB.setMemberValByReflection = function (targetObject, occurrency, propsArray, value) {
    var member;
	member = (occurrency != null) ? targetObject[occurrency]:targetObject;
    for (var idx = 0; idx < propsArray.length -1; idx++) {
        member = member[propsArray[idx]];
    }
    member[propsArray[propsArray.length - 1]] = value;
}

// Reflection getter 
jQXB.getMemberByReflection = function (targetObject, occurrency, propsArray) {
    var member;
	member = (occurrency != null) ? targetObject[occurrency]:targetObject;
    for (var idx = 0; idx < propsArray.length - 1; idx++) {
        member = member[propsArray[idx]];
    }
    return member[propsArray[propsArray.length - 1]];
}

// get the value from binder 
// param: internalObject    = the instance of the object stored in the binder collection
// param: occurency         = specify the n-element of the list stored in the binder ( used by template binding )
// param: internalVarMember = the name of the member binded to the single HTML element wrapped in a jQyery element 
// param: jQryObject        = the jQuery object representing the HTML binded to the single member
jQXB.getmemberValue = function (internalObject, occurency, internalVarmember, jQryObject) {
    var Member;
    Member = jQXB.getMemberByReflection(internalObject, occurency, internalVarmember.split('.'));
    var attribute = jQryObject.attr(jQXB.JQXB_BINDEDATTRIBUTE_ATTR);
    if (typeof (Member) == 'function')
        Member = Member(internalObject[occurency] || internalObject);
    if (attribute == undefined)
        jQryObject.val(Member);
    else {
        switch (attribute) {
            case "html":
                jQryObject.html(Member);
                break;
            case "text":
                jQryObject.text(Member);
                break;
            default:
                jQryObject.attr(attribute, Member);
                break;
        }
    }
    Member = null;
    return jQXB;
}

// Retrieve the correct value from HTML element
//depending on jQXB.JQXB_BINDEDATTRIBUTE_ATTR setting
jQXB.getValueFromAttrib = function (jQrjElem) {
    var attrib = jQrjElem.attr(jQXB.JQXB_BINDEDATTRIBUTE_ATTR);
    if (attrib == undefined)
        return jQrjElem.attr(attrib);
    else
        return jQrjElem.val();
}


/**********************************************************
*  Helpers
**********************************************************/
jQXB.utils = {}

jQXB.utils.filllist = function (jQrjElement, dataItems, valueMember, textMember) {
    if (!jQXB.utils.isEnumerable(dataItems)) {
        alert('jQXB.utils.fillcomdo: dataItems is not an enumerable type')
        return;
    }
    var currvalue = jQrjElement.val();
    jQrjElement.find('option').remove();
    for (var i = 0; i < dataItems.length; i++) {
        jQrjElement.append(jQuery('<option></option>').
					attr('value', jQXB.getMemberByReflection(dataItems, i, valueMember.split('.'))).
					text(jQXB.getMemberByReflection(dataItems, i, textMember.split('.'))));
    }
    jQrjElement.val(currvalue);
}

jQXB.utils.isEnumerable = function (obj) {
    return obj.length != undefined;
}

jQXB.utils.normalizeMemberPath = function (memberpath) {
    return memberpath.replace('[').replace(']');
}


jQXB.utils.makeObservable = function (objSource) {
    var obj = {};
    for (var member in objSource) {
        obj.__defineGetter__(member.toString(), function () {
            return member;
        });
        obj._defineSetter__(member.toString(), function (value) {
            member = value;
        });
    }
}

/*********************************************************
*  DIAGS
**********************************************************/
jQXB.diags = {MAX_DUMP_DEPTH: 10};
//
//
jQXB.diags.dumpobj = function (obj, name, indent, maxdepth) {
    depth = maxdepth || 0;
    if (depth > jQXB.diags.MAX_DUMP_DEPTH) {
        return indent + name + ": <Maximum Depth Reached>\n";
    }
    if (typeof obj == "object") {
        var child = null;
        var output = indent + name + "\n";
        indent += "\t";
        for (var item in obj) {
            try {
                child = obj[item];
            } catch (e) {
                child = "<Unable to Evaluate>";
            }
            if (typeof child == "object") {
                output += jQXB.diags.dumpobj(child, item, indent, depth + 1);
            } else {
                output += indent + item + ": " + child + "\n";
            }
        }
        return output;
    } else {
        return obj;
    }
}

jQXB.diags.output = function (obj) {
    //Optput however you want   
    alert(obj);
}

/**********************************************************
* Messaging subsystem
**********************************************************/
jQXBM = {
    messageSubscribers: new Array(),
    checkNoSubscriber: false
}
// Subscribe a Message
jQXBM.subscribeMessage = function (topic, messageHandler) {
    topic = topic || 'any';
    if (typeof (messageHandler) != 'function') {
        alert("jQXBM.subscribeMessage: messagehandler for topic [" + topic + "] is not a function");
        return;
    }
    jQXBM.messageSubscribers[topic] = jQXBM.messageSubscribers[topic] || new Array();
    for (idx = 0; idx < jQXBM.messageSubscribers[topic].length; idx++) {
        if (jQXBM.messageSubscribers[topic][idx].toString() == messageHandler.toString())
            return;
    }
    jQXBM.messageSubscribers[topic].push(messageHandler);
}

jQXBM.unsubscribeMessage = function (topic, messageHandler) {
    topic = topic || 'any';
    if (typeof (messageHandler) != 'function') {
        alert("jQXBM.unsubscribeMessage: messagehandler for topic [" + topic + "] is not a function");
        return;
    }
	
	for (idx = 0; idx < jQXBM.messageSubscribers[topic].length; idx++) {
        if (jQXBM.messageSubscribers[topic][idx].toString() == messageHandler.toString())
			jQXBM.messageSubscribers[topic].splice(idx, 1);
	}
}

jQXBM.fireMessage = function (topic, argument, sender) {
    var subscribers;
    // First notifies generic handler listening for "any" messages
    subscribers = jQXBM.messageSubscribers['any'];
    if (subscribers != undefined) {
        for (i = 0; i < subscribers.length; i++) {
            subscribers[i](argument, sender);
        }
    }
    // Then notifies the handlers for the specific message
    if (topic == undefined)
        return;
    subscribers = jQXBM.messageSubscribers[topic];
    if (subscribers == undefined)
        return;
    for (i = 0; i < subscribers.length; i++) {
        subscribers[i](argument, sender);
    }
}

