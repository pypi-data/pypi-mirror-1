<ul xmlns:py='http://purl.org/kid/ns#'
    class="checkselect"
    id="${field_id}"
    py:attrs="list_attrs">
    <li py:for="value, desc, attrs in options">
        <label for="${field_id}_${value}">
            <input type="checkbox"
                   id="${field_id}_${value}"
                   name="${name}"
                   value="${value}"
                   py:attrs="attrs"
            />${desc}</label>
    </li>
</ul>