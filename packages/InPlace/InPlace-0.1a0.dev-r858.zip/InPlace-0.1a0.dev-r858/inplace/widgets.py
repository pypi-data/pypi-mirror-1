import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

from scriptaculous import prototype_js

js_dir = pkg_resources.resource_filename("inplace",
                                         "static/javascript")
register_static_directory("inplace", js_dir)

inplace_js = JSLink('inplace', 'inplace.js')

class InPlace(Widget):
    javascript = [prototype_js, inplace_js]

inplace = InPlace()

class InPlaceDesc(WidgetDescription):
    for_widget = inplace
    show_separately = True
    template = """<div xmlns:py="http://purl.org/kid/ns#">
        <div style="font-size: x-large;" id="editable_title_1">Click here to edit this!</div>
        
        <br/>
        
        <div style="font-size: x-large;" id="editable_title_2">Prefixed Title 1</div>

        <select id="title_selector" 
                style="visibility: hidden; position: absolute;">
            <option>Prefixed Title 1</option>
            <option>Prefixed Title 2</option>
            <option>Prefixed Title 3</option>
        </select>
        
        <br/>
        
        <table id="inplace_test_table" border="1" align="center" bgcolor="white">
        </table>
        
        <script type="text/javascript">
            function onload() {
                // populate the table and add editors for each cell
                test_table = $$('inplace_test_table');
                for (var row=0; row != 5; row++) {
                    tr = document.createElement('tr');
                    for (var col=0; col != 5; col++) {
                        td = document.createElement('td');
                        td.innerHTML = 'cell ' + (row + 1) + 'x' + (col + 1);
                        tr.appendChild(td);
                        new InPlace(td);
                    }
                    test_table.appendChild(tr);
                }
                
                // add editors for titles
                new InPlace('editable_title_1');
                new InPlace('editable_title_2', 
                            {'field': new SingleSelectField('title_selector')});
            }
            Event.observe(window, 'load', onload);
        </script>
        
    </div>
    """
    
        
        