<%args>
    form
</%args>

<h3>ZBlog Login</h3>

<&|/components:entryform, name="mainform", columns=2, action="/login/login/"&>
    <&|/components:field, type="text", field=form['username']&>
        Username
    </&>
    <&|/components:field, type="password", field=form['password']&>
        Password
    </&>
    <&|/components:row&>
    <&/components:field, type="submit", value="Login"&>
    </&>
</&>


<%method status>
    <%args scope="subrequest">
        form
    </%args>
<&PARENT:status&>
<h3><& /form:formstatus, form=form,  &></h3>
</%method>
