<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}"
    action="${action}"
    method="${method}"
    class="tableform"
    accept-charset="UTF-8"
    py:attrs="form_attrs"
>
    <div py:for="field in hidden_fields" 
        py:replace="field.display(value_for(field), **params_for(field))" 
    />
    <table border="0" cellspacing="0" cellpadding="2" py:attrs="table_attrs">
        <tr py:for="i, field in enumerate(fields)" 
            class="${i%2 and 'odd' or 'even'}"
        >
            <th>
                <label class="fieldlabel" for="${field.field_id}" py:content="field.label" />
            </th>
            <td>
                <span py:replace="field.display(value_for(field), **params_for(field))" />
                <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
                <span py:if="field.help_text" class="fieldhelp" py:content="field.help_text" />
            </td>
        </tr>
        <tr>
            <td>&#160;</td>
            <td py:content="submit.display(submit_text)" />
        </tr>
    </table>
</form>
