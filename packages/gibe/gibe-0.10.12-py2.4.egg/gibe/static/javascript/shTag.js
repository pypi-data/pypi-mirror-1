// highlightes all elements identified by name and gets source code from specified property
dp.sh.HighlightTag = function(tag, showGutter /* optional */, showControls /* optional */, collapseAll /* optional */, firstLine /* optional */, showColumns /* optional */)
{
	function FindValue()
	{
		var a = arguments;
		
		for(var i = 0; i < a.length; i++)
		{
			if(a[i] == null)
				continue;
				
			if(typeof(a[i]) == 'string' && a[i] != '')
				return a[i] + '';
		
			if(typeof(a[i]) == 'object' && a[i].value != '')
				return a[i].value + '';
		}
		
		return null;
	}
	
	function IsOptionSet(value, list)
	{
		for(var i = 0; i < list.length; i++)
			if(list[i] == value)
				return true;
		
		return false;
	}
	
	function GetOptionValue(name, list, defaultValue)
	{
		var regex = new RegExp('^' + name + '\\[(\\w+)\\]$', 'gi');
		var matches = null;

		for(var i = 0; i < list.length; i++)
			if((matches = regex.exec(list[i])) != null)
				return matches[1];
		
		return defaultValue;
	}

	var initial_elements = document.getElementsByTagName(tag);
        var elements = [];

        for (var i = 0; i < initial_elements.length; i++) {
            el = initial_elements[i];
            if (!el.className) {
                continue;
            }
	    var options = FindValue(el.className);
	    options = options.split(' ');
            for (var j = 0; j < options.length; j++) {
                if (options[j] == "dp::syntaxhighlight") {
                    elements.push(el);
                }
            }
        }

           
	var highlighter = null;
	var registered = new Object();
	var propertyName = 'textContent';
	
	// if no code blocks found, leave
	if(elements == null)
		return;

	// register all brushes
	for(var brush in dp.sh.Brushes)
	{
		var aliases = dp.sh.Brushes[brush].Aliases;

		if(aliases == null)
			continue;
		
		for(var i = 0; i < aliases.length; i++)
			registered[aliases[i]] = brush;
	}

	for(var i = 0; i < elements.length; i++)
	{
		var element = elements[i];
		var options = FindValue(
				element.attributes['class'], element.className, 
				element.attributes['language'], element.language
				);
		var language = '';
		
		if(options == null)
			continue;
		
		classes = options.split(' ');
		
                language = null;
                
		for (var j = 0; j < classes.length; j++) {
			if(registered[classes[j]] == null)
				continue;
			language = classes[j];
			break;
		}

		if(language == null)
			continue;

		// instantiate a brush
		highlighter = new dp.sh.Brushes[registered[language]]();
		
		// hide the original element
		element.style.display = 'none';

		highlighter.noGutter = (showGutter == null) ? IsOptionSet('nogutter', options) : !showGutter;
		highlighter.addControls = (showControls == null) ? !IsOptionSet('nocontrols', options) : showControls;
		highlighter.collapse = (collapseAll == null) ? IsOptionSet('collapse', options) : collapseAll;
		highlighter.showColumns = (showColumns == null) ? IsOptionSet('showcolumns', options) : showColumns;
		
		// first line idea comes from Andrew Collington, thanks!
		highlighter.firstLine = (firstLine == null) ? parseInt(GetOptionValue('firstline', options, 1)) : firstLine;

		last_element = element;
		highlighter.Highlight(element[propertyName]);

		element.parentNode.insertBefore(highlighter.div, element);
	}	
}
var last_element;
