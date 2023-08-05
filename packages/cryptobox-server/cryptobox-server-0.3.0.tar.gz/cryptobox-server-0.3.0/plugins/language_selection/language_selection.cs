<?cs # $Id: language_selection.cs 747 2007-02-03 18:24:07Z age $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.language_selection.Title.Lang) ?>
	</legend>

<?cs call:show_help(Lang.Plugins.language_selection.Help.Select) ?>

	<ul class="lang">
		<?cs loop:index = #0, subcount(Data.Languages)-1, #1 ?>
			<li><a href="<?cs
				call:link("language_selection", 'weblang', Data.Languages[index].name, '','') ?>" title="<?cs
				var:html_escape(Data.Languages[index].link) ?>" ><?cs
				var:html_escape(Data.Languages[index].link) ?></a>
				<?cs if:Settings.Language == Data.Languages[index].name ?>
					&nbsp;<img src="icons/language_selection?image=list_marker_tango.gif"
						alt="symbol: current language" style="vertical-align:middle" />
				<?cs /if ?>
				</li><?cs /loop ?>
	</ul>
</fieldset>
