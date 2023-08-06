JSonAutoComplete = function (id, container, url){
        this.dataSource = new YAHOO.util.XHRDataSource(url, {
            responseType: YAHOO.util.XHRDataSource.TYPE_JSON,
            responseSchema: {resultsList:'results.items',
                             fields: ['title'],}}
                             );
        this.autoComplete = new YAHOO.widget.AutoComplete(id, container, this.dataSource,{
                queryDelay: 0.5,
                generateRequest: function(sQuery) {
                return "?query=" + sQuery ;
                        }
                });
}