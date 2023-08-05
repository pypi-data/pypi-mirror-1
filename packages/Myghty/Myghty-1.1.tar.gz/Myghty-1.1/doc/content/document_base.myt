<%flags>inherit="doclib.myt"</%flags>

<%python scope="global">

    files = [
        'whatsitdo',
        'installation',
        'configuration',
        'programmatic',
        'embedding',
        'scopedpython',
        'globals',
        'components',
        'modulecomponents',
        'request',
        'otherblocks',
        'inheritance',
        'specialtempl',
        'filtering',
        'session',
        'cache',
        'resolver',
	'unicode',
        'params',
        'technical',
        'docstrings'
        ]

</%python>

<%attr>
    files=files
    wrapper='section_wrapper.myt'
    onepage='documentation'
    index='index'
    title='Myghty Documentation'
    version = '1.1'
</%attr>






