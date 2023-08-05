<%args>
    form
</%args>

<h2>Register for ZBlog!</h2>
<&|/components:entryform, form=form, columns=2&>
    <&/components:field, type="hidden", name="validate", value="1"&>
    <&|/components:field, type="text", name='name' &>
        User Name
    </&>
    <&|/components:field, type="text", name='fullname'&>
        Full Name
    </&>
    <&|/components:field, type="password", name='password_set'&>
        Password
    </&>
    <&|/components:field, type="password", name='password_repeat'&>
        Repeat Password
    </&>
    <&|/components:row, colspan="2" &>
    <&/components:field, type="submit", value="Register"&>
    </&>
    
</&>    


<%method status>
    <%args scope="subrequest">
        form
    </%args>
<&PARENT:status&>
<h3><& /form:formstatus, form=form,  &></h3>
</%method>
