<div>
    <div id="${id}_autocomplete" style="height:2em"> 
        <input id="${id}" type="text" name="${name}" value="${value}"/>
        <div id="${id}_autocomplete_container"></div> 
    </div> 
    <script type="text/javascript"> 
        ${id}_autocomplete = new JSonAutoComplete("${id}", "${id}_autocomplete_container", "${url}");
    </script>
</div>