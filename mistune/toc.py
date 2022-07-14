from .util import striptags


def add_toc_hook(md, level=3, heading_id=None):
    """Add a hook to save toc items into ``state.env``::

        import mistune
        from mistune.toc import add_toc_hook, render_toc_ul

        md = mistune.create_markdown(...)
        add_toc_hook(md, level, heading_id)

        html, state = md.parse(text)
        toc_items = state.env['toc_items']
        toc_html = render_toc_ul(toc_items)
    """
    if heading_id is None:
        def heading_id(token, index):
            return 'toc_' + str(index + 1)

    def toc_hook(md, state):
        headings = []

        for tok in state.tokens:
            if tok['type'] == 'heading' and tok['attrs']['level'] <= level:
                headings.append(tok)

        toc_items = []
        for i, tok in enumerate(headings):
            tok['attrs']['id'] = heading_id(tok, i)
            toc_items.append(normalize_toc_item(md, tok))

        # save items into state
        state.env['toc_items'] = toc_items

    md.before_render_hooks.append(toc_hook)


def normalize_toc_item(md, token):
    text = token['text']
    html = md.inline(text, {})
    text = striptags(html)
    attrs = token['attrs']
    return attrs['level'], attrs['id'], text


def render_toc_ul(toc):
    """Render a <ul> table of content HTML. The param "toc" should
    be formatted into this structure::

        [
          (level, id, text),
        ]

    For example::

        [
          (1, 'toc-intro', 'Introduction'),
          (2, 'toc-install', 'Install'),
          (2, 'toc-upgrade', 'Upgrade'),
          (1, 'toc-license', 'License'),
        ]
    """
    if not toc:
        return ''

    s = '<ul>\n'
    levels = []
    for level, k, text in toc:
        item = '<a href="#{}">{}</a>'.format(k, text)
        if not levels:
            s += '<li>' + item
            levels.append(level)
        elif level == levels[-1]:
            s += '</li>\n<li>' + item
        elif level > levels[-1]:
            s += '\n<ul>\n<li>' + item
            levels.append(level)
        else:
            last_level = levels.pop()
            while levels:
                last_level = levels.pop()
                if level == last_level:
                    s += '</li>\n</ul>\n</li>\n<li>' + item
                    levels.append(level)
                    break
                elif level > last_level:
                    s += '</li>\n<li>' + item
                    levels.append(last_level)
                    levels.append(level)
                    break
                else:
                    s += '</li>\n</ul>\n'
            else:
                levels.append(level)
                s += '</li>\n<li>' + item

    while len(levels) > 1:
        s += '</li>\n</ul>\n'
        levels.pop()

    return s + '</li>\n</ul>\n'
