/* Import plugin specific language pack */
tinyMCE.importPluginLanguagePack('insertexcerptline', 'en');

var TinyMCE_InsertExcerptLinePlugin = {
	getInfo : function() {
		return {
			longname : 'Insert Excerpt Line',
			author : 'Neil Blakey-Milner',
			authorurl : 'http://nxsy.org/',
			infourl : 'http://nxsy.org/code/gibe/',
			version : "0.1"
		};
	},

	/**
	 * Returns the HTML contents of the insertdate, inserttime controls.
	 */
	getControlHTML : function(cn) {
		switch (cn) {
			case "insertexcerptline":
				return tinyMCE.getButtonHTML(cn, 'lang_insertexcerptline_desc', '{$pluginurl}/images/insertdate.gif', 'mceInsertExcerptLine');
		}

		return "";
	},

	/**
	 * Executes the mceInsertExcerptLine command.
	 */
	execCommand : function(editor_id, element, command, user_interface, value) {
		// Handle commands
		switch (command) {
			case "mceInsertExcerptLine":
				tinyMCE.execInstanceCommand(editor_id, 'mceInsertContent', false, '<hr class="excerpt"></hr>');
				return true;

		}

		// Pass to next handler in chain
		return false;
	}
};

tinyMCE.addPlugin("insertexcerptline", TinyMCE_InsertExcerptLinePlugin);
