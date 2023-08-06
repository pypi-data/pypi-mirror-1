<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}"
    action="${action}"
    method="${method}"
    class="listform"
    py:attrs="form_attrs"
>
    <div py:for="field in hidden_fields" 
        py:replace="field.display(value_for(field), **params_for(field))" 
    />
    <div py:attrs="list_attrs">
        <div py:for="i, field in enumerate(fields)" 
            class="${i%2 and 'odd' or 'even'}"
        >
            <label py:if="hasattr(field, 'label')" class="fieldlabel" for="${field.field_id}" py:content="field.label" />
            <span py:replace="field.display(value_for(field), **params_for(field))" />
            <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
            <span py:if="hasattr(field, 'help_text') and field.help_text" class="fieldhelp" py:content="field.help_text" />
        </div>
        <div py:content="submit.display(submit_text)" />
    </div>
</form>
