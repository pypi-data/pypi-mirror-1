<div xmlns:py="http://purl.org/kid/ns#"
        name="${name}"
        class="tableform"
        py:attrs="form_attrs"
    >
    <div py:for="field in hidden_fields" 
        py:replace="field.display(value_for(field), **params_for(field))" 
    />
    <table py:attrs="table_attrs">
    <tbody>
        <tr py:for="i, field in enumerate(fields)" 
            class="${(i%2 and 'odd' or 'even') + (error_for(field) and ' fielderror' or ' ')}"
        >
            <th>
                <label py:if="hasattr(field, 'label')" class="fieldlabel" for="${field.field_id}" py:content="field.label" />
            </th>
            <td>
                <span py:replace="field.display(value_for(field), **params_for(field))" />
                <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
                <span py:if="field.help_text and not field.is_validated" 
                        class="fieldhelp" py:content="field.help_text" />
            </td>
        </tr>
        <tr>
            <td>&#160;</td>
        </tr>
    </tbody>
    </table>
</div>