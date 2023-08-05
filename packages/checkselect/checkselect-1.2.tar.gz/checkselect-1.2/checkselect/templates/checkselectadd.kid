<div xmlns:py='http://purl.org/kid/ns#'>
  <ul class="checkselect"
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
  <p>
    <a href='${link}' target='${target}'>
    <img border='0'
         align='middle'
         title='${text}'
         alt='${text}'
         src='${tg.url([tg.widgets, "checkselect/images/page_new.gif"])}'
         />
    ${text}
    </a>
  </p>
</div>