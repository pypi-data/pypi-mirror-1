<%python scope="global">
    import string, re, time

</%python>

<%args>
    comp
    toc
    title
    version = None
    last_updated = None
    index
    paged
    onepage
    isdynamic
    ext
</%args>


<link href="docs.css" rel="stylesheet" type="text/css"></link>


<div style="position:absolute;left:0px;top:0px;"><a name="top"></a>&nbsp;</div>

<div class="doccontainer">

<div class="docheader">

<div class="docheadertext" ><% title %></div>
% if version is not None:
<div class="">Version: <% version %>   Last Updated: <% time.strftime('%x %X', time.localtime(last_updated)) %></div>
%
</div>

<& printsection.myt, paged = paged, toc = toc, comp = comp, isdynamic=isdynamic, index=index, ext=ext,onepage=onepage &>

</div>


