
BASIC_FORM_CSS = """\
form.qp div.title {
    font-weight: bold;
}

form.qp br.submit,
form.qp br.widget,
br.qpform {
    clear: left;
}

form.qp div.submit br.widget {
    display: none;
}

form.qp div.widget {
    float: left;
    padding: 4px;
    padding-right: 1em;
    margin-bottom: 6px;
}

/* pretty forms (attribute selector hides from broken browsers (e.g. IE) */
form.qp[action] {
    float: left;
}

form.qp[action] > div.widget {
    float: none;
}

form.qp[action] > br.widget {
    display: none;
}

form.qp div.widget div.widget {
    padding: 0;
    margin-bottom: 0;
}

form.qp div.SubmitWidget {
    float: left
}

form.qp div.content {
    margin-left: 0.6em; /* indent content */
}

form.qp div.content div.content {
    margin-left: 0; /* indent content only for top-level widgets */
}

form.qp div.error {
    color: #c00;
    font-size: small;
    margin-top: .1em;
}

form.qp div.hint {
    font-size: small;
    font-style: italic;
    margin-top: .1em;
}

form.qp div.errornotice {
    color: #c00;
    padding: 0.5em;
    margin: 0.5em;
}

form.qp div.FormTokenWidget,
form.qp div.HiddenWidget {
    display: none;
}
"""
