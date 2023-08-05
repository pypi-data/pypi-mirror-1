<%doc>
    bootstrap/index.myt .  This template is designed to interact with the zblog.controller.bootstrap controller module and is used to get initial database config information.
</%doc>

<%init>
    # AJAX call definitions.  both ajax calls in this doc go to controllers.
    if m.comp('/ajax/myghtyjax.myt:init', 
        dboptions = {
                        'component':m.fetch_component('/bootstrap/ajax_dboptions', resolver_context='frontcontroller'),
                        'handler_uri':'/bootstrap/ajax_dboptions/', 
                        'exectype':'writedom', 
                        'dom_id':'dbtype'
                    },
        testconnect = {
            'component':m.fetch_component('/bootstrap/ajax_testconnect', resolver_context='frontcontroller'),
            'handler_uri':'/bootstrap/ajax_testconnect/',
            'exectype':'writedom',
            'dom_id':'dbtype'
        },
    ): return

</%init>
<%args>
    form
</%args>

<& /ajax/myghtyjax.myt:js &>

<h2>ZBLOG Bootstrap System</h2>

<p>This page is only viewed when you first install ZBLOG.</p>


<& /form:formstatus, form=form &>

<&|/components:entryform, action="/bootstrap/bootstrap/", columns=2, form=form&>
    <&|/components:field, type="text", name='adminuser'&>
        Administrator Username
    </&>
    <&|/components:field, type="text", name='adminpw'&>
        Administrator Password
    </&>
    <&|/components:field, type="dropdown", name='dbtype', onselect='dboptions'&>
        Database Type
    </&>
    <&|/components:popup, name="dbtype"&>
        <& SELF:dboptions, **ARGS &>
    </&>
</&>


<%method dboptions>
    <%doc>Displays the entry fields corresponding to a specific type of database, 
    if the given form contains a 'dbform' element, which is set by the controller. else just returns.
    </%doc>
    <%args scope="dynamic">
        form
        dbtype=None
        connected=False
        error=None
    </%args>
    <%init>
        if not dbtype: 
            return
        subform = form['dbform']
        formargs = m.scomp('/components:formargs', form=subform, name=form.name)
    </%init>
    <&|/components:fields&>
    <tr><td><h3><% subform.description %> Options</h3></td></tr>
% for field in subform:
        <&|/components:field, type="text", field=field &>
            <% field.description %>
        </&>
%
    </&>

% if error:
    <% str(error) %><br/>
%
% if not connected:
    <&/components:button, value="Connect", onclick="testconnect('%s', %s)" % (dbtype, formargs)  &>
% elif connected:
    Connected! 
    <input type="hidden" name="writefile" value="1">
    <input type="hidden" name="connected" value="1">
    <&/components:submit, value="Write Config File"  &>
%

</%method>


