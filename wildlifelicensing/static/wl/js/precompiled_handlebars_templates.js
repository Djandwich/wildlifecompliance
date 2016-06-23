define(["handlebars.runtime"],function(l){l=l["default"];var n=l.template,e=l.templates=l.templates||{};return e.section=n({compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s=null!=n?n:{},t=e.helperMissing,i="function",o=l.escapeExpression;return'<h3 id="section-'+o((u=null!=(u=e.index||(null!=n?n.index:n))?u:t,typeof u===i?u.call(s,{name:"index",hash:{},data:r}):u))+'" class="section">'+o((u=null!=(u=e.label||(null!=n?n.label:n))?u:t,typeof u===i?u.call(s,{name:"label",hash:{},data:r}):u))+"</h3>\r\n<hr>"},useData:!0}),e.checkbox=n({1:function(l,n,e,a,r){return"data-parsley-required"},3:function(l,n,e,a,r){return"checked"},5:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'<div class="form-group">\n    <input name="'+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'" type="checkbox" '+(null!=(u=e["if"].call(t,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+" "+(null!=(u=e["if"].call(t,null!=n?n.value:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+"> "+p((s=null!=(s=e.label||(null!=n?n.label:n))?s:i,typeof s===o?s.call(t,{name:"label",hash:{},data:r}):s))+"\n"+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(5,r,0),inverse:l.noop,data:r}))?u:"")+"</div>"},useData:!0}),e.radiobuttons=n({1:function(l,n,e,a,r,u,s){var t,i=l.lambda,o=l.escapeExpression,p=null!=n?n:{};return'        <div class="radio">\n            <label>\n                <input name="'+o(i(null!=s[1]?s[1].name:s[1],n))+'" type="radio" value="'+o(i(null!=n?n.value:n,n))+'" '+(null!=(t=e["if"].call(p,null!=s[1]?s[1].required:s[1],{name:"if",hash:{},fn:l.program(2,r,0,u,s),inverse:l.noop,data:r}))?t:"")+" "+(null!=(t=(e.isEqual||n&&n.isEqual||e.helperMissing).call(p,null!=n?n.value:n,null!=s[1]?s[1].value:s[1],{name:"isEqual",hash:{},fn:l.program(4,r,0,u,s),inverse:l.noop,data:r}))?t:"")+">\n                "+o(i(null!=n?n.label:n,n))+"\n            </label>\n        </div>\n"},2:function(l,n,e,a,r){return"required"},4:function(l,n,e,a,r){return"checked"},6:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r,u,s){var t,i,o=null!=n?n:{};return'<div class="form-group">\n    <label >'+l.escapeExpression((i=null!=(i=e.label||(null!=n?n.label:n))?i:e.helperMissing,"function"==typeof i?i.call(o,{name:"label",hash:{},data:r}):i))+"</label>\n"+(null!=(t=e.each.call(o,null!=n?n.options:n,{name:"each",hash:{},fn:l.program(1,r,0,u,s),inverse:l.noop,data:r}))?t:"")+(null!=(t=e["if"].call(o,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(6,r,0,u,s),inverse:l.noop,data:r}))?t:"")+"</div>"},useData:!0,useDepths:!0}),e.select=n({1:function(l,n,e,a,r){return"required"},3:function(l,n,e,a,r){return'            <option disabled selected value=" ">Please Choose</option>\r\n'},5:function(l,n,e,a,r,u,s){var t,i=l.lambda,o=l.escapeExpression;return'            <option value="'+o(i(null!=n?n.value:n,n))+'" class="form-control" '+(null!=(t=(e.isEqual||n&&n.isEqual||e.helperMissing).call(null!=n?n:{},null!=n?n.value:n,null!=s[1]?s[1].value:s[1],{name:"isEqual",hash:{},fn:l.program(6,r,0,u,s),inverse:l.noop,data:r}))?t:"")+">"+o(i(null!=n?n.label:n,n))+"</option>\r\n"},6:function(l,n,e,a,r){return"selected"},8:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\r\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r,u,s){var t,i,o=null!=n?n:{},p=e.helperMissing,c="function",h=l.escapeExpression;return'<div class="form-group">\r\n    <label>'+h((i=null!=(i=e.label||(null!=n?n.label:n))?i:p,typeof i===c?i.call(o,{name:"label",hash:{},data:r}):i))+' </label>\r\n    <select name="'+h((i=null!=(i=e.name||(null!=n?n.name:n))?i:p,typeof i===c?i.call(o,{name:"name",hash:{},data:r}):i))+'" class="form-control" '+(null!=(t=e["if"].call(o,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(1,r,0,u,s),inverse:l.noop,data:r}))?t:"")+">\r\n"+(null!=(t=e["if"].call(o,null!=n?n.defaultBlank:n,{name:"if",hash:{},fn:l.program(3,r,0,u,s),inverse:l.noop,data:r}))?t:"")+(null!=(t=e.each.call(o,null!=n?n.options:n,{name:"each",hash:{},fn:l.program(5,r,0,u,s),inverse:l.noop,data:r}))?t:"")+"    </select>\r\n"+(null!=(t=e["if"].call(o,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(8,r,0,u,s),inverse:l.noop,data:r}))?t:"")+"</div>"},useData:!0,useDepths:!0}),e.label=n({1:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\r\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{};return'<div class="form-group">\r\n    <label >'+l.escapeExpression((s=null!=(s=e.label||(null!=n?n.label:n))?s:e.helperMissing,"function"==typeof s?s.call(t,{name:"label",hash:{},data:r}):s))+" </label>\r\n"+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+" </div>"},useData:!0}),e.text=n({1:function(l,n,e,a,r){return"required"},3:function(l,n,e,a,r){var u;return'value="'+l.escapeExpression((u=null!=(u=e.value||(null!=n?n.value:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"value",hash:{},data:r}):u))+'"'},5:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\r\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'<div class="form-group">\r\n    <label >'+p((s=null!=(s=e.label||(null!=n?n.label:n))?s:i,typeof s===o?s.call(t,{name:"label",hash:{},data:r}):s))+' </label>\r\n    <input name="'+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'" class="form-control" '+(null!=(u=e["if"].call(t,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+" "+(null!=(u=e["if"].call(t,null!=n?n.value:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+"/>\r\n"+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(5,r,0),inverse:l.noop,data:r}))?u:"")+" </div>"},useData:!0}),e.declaration=n({1:function(l,n,e,a,r){return"data-parsley-required"},3:function(l,n,e,a,r){return"checked"},5:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'<div class="form-group">\n    <label>\n        <input name="'+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'" type="checkbox" '+(null!=(u=e["if"].call(t,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+" "+(null!=(u=e["if"].call(t,null!=n?n.value:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+">\n        "+p((s=null!=(s=e.label||(null!=n?n.label:n))?s:i,typeof s===o?s.call(t,{name:"label",hash:{},data:r}):s))+"\n    </label> \n"+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(5,r,0),inverse:l.noop,data:r}))?u:"")+"</div>"},useData:!0}),e.group=n({1:function(l,n,e,a,r){var u,s=null!=n?n:{};return(null!=(u=e["if"].call(s,null!=n?n.isRepeatable:n,{name:"if",hash:{},fn:l.program(2,r,0),inverse:l.noop,data:r}))?u:"")+'                <div class="remove pull-right '+(null!=(u=e.unless.call(s,null!=n?n.isRemovable:n,{name:"unless",hash:{},fn:l.program(4,r,0),inverse:l.noop,data:r}))?u:"")+'">\n                    <a>Remove</a>\n                </div>\n'},2:function(l,n,e,a,r){var u;return'                    <a class="copy">Copy '+l.escapeExpression((u=null!=(u=e.label||(null!=n?n.label:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"label",hash:{},data:r}):u))+"</a>\n"},4:function(l,n,e,a,r){return"hidden"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{};return"<div>\n    <h4>"+l.escapeExpression((s=null!=(s=e.label||(null!=n?n.label:n))?s:e.helperMissing,"function"==typeof s?s.call(t,{name:"label",hash:{},data:r}):s))+'</h4>\n    <div class="panel panel-default">\n        <div class="panel-body">\n            <div class="children-anchor-point" style="padding-left: 0px">\n            </div>\n'+(null!=(u=e.unless.call(t,null!=n?n.isPreviewMode:n,{name:"unless",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+"        </div>\n    </div>\n</div>"},useData:!0}),e.text_area=n({1:function(l,n,e,a,r){return"required"},3:function(l,n,e,a,r){var u;return l.escapeExpression((u=null!=(u=e.value||(null!=n?n.value:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"value",hash:{},data:r}):u))},5:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\r\n"},7:function(l,n,e,a,r){var u;return"        <span class=\"glyphicon glyphicon-remove form-control-feedback\"></span>\r\n        <span class='text-danger'>"+l.escapeExpression((u=null!=(u=e.errors||(null!=n?n.errors:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"errors",hash:{},data:r}):u))+"</span>\r\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'<div class="form-group">\r\n    <label>'+p((s=null!=(s=e.label||(null!=n?n.label:n))?s:i,typeof s===o?s.call(t,{name:"label",hash:{},data:r}):s))+' </label>\r\n    <textarea rows="3" name="'+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'" class="form-control" '+(null!=(u=e["if"].call(t,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+">"+(null!=(u=e["if"].call(t,null!=n?n.value:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+"</textarea>\r\n"+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(5,r,0),inverse:l.noop,data:r}))?u:"")+(null!=(u=e["if"].call(t,null!=n?n.errors:n,{name:"if",hash:{},fn:l.program(7,r,0),inverse:l.noop,data:r}))?u:"")+" </div>"},useData:!0}),e.file=n({1:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'        <p>\n            Currently: <a href="'+p((s=null!=(s=e.value||(null!=n?n.value:n))?s:i,typeof s===o?s.call(t,{name:"value",hash:{},data:r}):s))+'" target="_blank">'+(null!=(u=(e.getURLFilename||n&&n.getURLFilename||i).call(t,null!=n?n.value:n,{name:"getURLFilename",hash:{},data:r}))?u:"")+'</a>\n        </p>\n        <input name="'+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'-existing" type="hidden" value="'+(null!=(u=(e.getURLFilename||n&&n.getURLFilename||i).call(t,null!=n?n.value:n,{name:"getURLFilename",hash:{},data:r}))?u:"")+'"/>\n'},3:function(l,n,e,a,r){var u;return'accept="'+l.escapeExpression((u=null!=(u=e.fileTypes||(null!=n?n.fileTypes:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"fileTypes",hash:{},data:r}):u))+'"'},5:function(l,n,e,a,r){return"required"},7:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'<div class="form-group">\n    <label>'+p((s=null!=(s=e.label||(null!=n?n.label:n))?s:i,typeof s===o?s.call(t,{name:"label",hash:{},data:r}):s))+"</label>\n"+(null!=(u=e["if"].call(t,null!=n?n.value:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+'    <input name="'+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'" type="file" class="form-control" '+(null!=(u=e["if"].call(t,null!=n?n.file_types:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+" "+(null!=(u=e["if"].call(t,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(5,r,0),inverse:l.noop,data:r}))?u:"")+"\n        "+(null!=(u=e["if"].call(t,null!=n?n.fileTypes:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+" >\n"+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(7,r,0),inverse:l.noop,data:r}))?u:"")+"</div>"},useData:!0}),e.date=n({1:function(l,n,e,a,r){return"required"},3:function(l,n,e,a,r){var u;return'value="'+l.escapeExpression((u=null!=(u=e.value||(null!=n?n.value:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"value",hash:{},data:r}):u))+'"'},5:function(l,n,e,a,r){var u;return'        <p class="help-block">'+l.escapeExpression((u=null!=(u=e.help_text||(null!=n?n.help_text:n))?u:e.helperMissing,"function"==typeof u?u.call(null!=n?n:{},{name:"help_text",hash:{},data:r}):u))+"</p>\n"},compiler:[7,">= 4.0.0"],main:function(l,n,e,a,r){var u,s,t=null!=n?n:{},i=e.helperMissing,o="function",p=l.escapeExpression;return'<div class="form-group">\n    <label>'+p((s=null!=(s=e.label||(null!=n?n.label:n))?s:i,typeof s===o?s.call(t,{name:"label",hash:{},data:r}):s))+"</label>\n    <div class='input-group date' id='"+p((s=null!=(s=e.id||(null!=n?n.id:n))?s:i,typeof s===o?s.call(t,{name:"id",hash:{},data:r}):s))+"-datetimepicker'>\n        <input name=\""+p((s=null!=(s=e.name||(null!=n?n.name:n))?s:i,typeof s===o?s.call(t,{name:"name",hash:{},data:r}):s))+'" class="form-control" placeholder="DD/MM/YYYY" '+(null!=(u=e["if"].call(t,null!=n?n.required:n,{name:"if",hash:{},fn:l.program(1,r,0),inverse:l.noop,data:r}))?u:"")+" "+(null!=(u=e["if"].call(t,null!=n?n.value:n,{name:"if",hash:{},fn:l.program(3,r,0),inverse:l.noop,data:r}))?u:"")+'/>\n        <span class="input-group-addon">\n            <span class="glyphicon glyphicon-calendar"></span>\n        </span>\n    </div>\n'+(null!=(u=e["if"].call(t,null!=n?n.help_text:n,{name:"if",hash:{},fn:l.program(5,r,0),inverse:l.noop,data:r}))?u:"")+"</div>"},useData:!0}),e});