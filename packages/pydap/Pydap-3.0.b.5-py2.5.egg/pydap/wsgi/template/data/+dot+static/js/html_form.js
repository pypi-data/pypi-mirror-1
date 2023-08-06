$(document).ready(function(){
    // Add more selections to filter sequences.
    var re = /(.*)\[(\d+)\]/;
    $('p.filter:last > select.var1').change(function() {
        if (this.value != '--') {
            var snippet = $(this.parentNode).clone(true);
            // Replace ids with unique ones.
            snippet.find('.var1,.op,.var2').each(function() {
                match = re.exec(this.id);
                base = match[1];
                counter = parseInt(match[2]) + 1;
                this.name = this.id = base + '[' + counter + ']';
            });
            snippet.insertAfter(this.parentNode);
            $(this).unbind('change');
        }
    });
});
