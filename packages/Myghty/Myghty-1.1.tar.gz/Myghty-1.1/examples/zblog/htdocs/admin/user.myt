<%method ajax>
<%init>
    return m.comp('/ajax/myghtyjax.myt:init', 
            useradmin={
                'handler_uri':'/manage/user/ajax_edituser/',
                'exectype':'writedom', 
                'dom_id':'opwindow'
            },
            action_edituser={
                'handler_uri':'/manage/user/edit_user/',
                'exectype':'writedom', 
                'dom_id':'opwindow'
            },
            action_deluser={
            'handler_uri':'/manage/user/delete_user/',
            'exectype':'writedom', 
            'dom_id':'opwindow'
            }
        )
</%init>
</%method>


<%method links>
% for link in [('javascript:useradmin()', 'User Administration')]:
<% m.content(url=link[0], text=link[1]) %>
%
</%method>

<%method userform>
    <%args>
        form
    </%args>

<& /form:formstatus, form=form &>

<&|/components:entryform, name="lookupform", onsubmit="useradmin({'username':document.lookupform.username.value});return false;", columns=2&>
    <tr>
        <td>
            Lookup User:
        </td>
        <td>
            <&/components:field, type="text", name="username"&>
            <&/components:field, type="submit", value="Find"&>
        </td>
    </tr>
</&>

<&|/components:entryform, ajaxtarget="action_edituser", form=form, columns=2&>
    <&/components:field, type="hidden", name='user_id'&>
    <&|/components:field, type="text", name='name' &>
        User Name
    </&>
    <&|/components:field, type="text", name='fullname'&>
        Full Name
    </&>
    <&|/components:field, type="dropdown", name='group'&>
        Group
    </&>
    <&|/components:field, type="password", name='password_set'&>
        Password
    </&>
    <&|/components:field, type="password", name='password_repeat'&>
        Repeat Password
    </&>
    <&|/components:row, colspan="2" &>
% if form['user_id'].value:
        <&/components:field, type="submit", value="Update User"&>
        <&/components:field, type="button", value="Delete User", onclick=m.comp('/components:ajaxaction', target="action_deluser", form=form) &>
% else:
    <&/components:field, type="submit", value="Create User"&>
%
    </&>
    
</&>    
</%method>

<%method delete_confirm>
    <%args>
        user
    </%args>
    <&|/components:confirm, yes="action_deluser({'user_id':'%s','confirm':1})" % user.id, 
                no="useradmin({'username':'%s'})" % user.name&>
    Are you sure you want to delete user '<% user.fullname %>'?
    This also deletes all blogs and posts by that user.
    </&>
</%method>