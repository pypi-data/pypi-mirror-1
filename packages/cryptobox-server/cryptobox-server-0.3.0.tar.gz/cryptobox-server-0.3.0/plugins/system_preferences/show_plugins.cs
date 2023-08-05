<?cs # $Id: show_plugins.cs 747 2007-02-03 18:24:07Z age $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.system_preferences.Title.Prefs) ?>
	</legend>

<?cs # sort the Plugins - using the most stupid way :) ?>
<?cs loop: order = #0, #100, #1
	?><?cs # plugins ?><?cs each:x = Settings.PluginList
		?><?cs if:x.Types.system && x.Visible.preferences && x.Rank == order ?>
			<div class="plugin_system ?>"><a href="<?cs
				call:link(name(x),'','','','') ?>" title="<?cs
				var:html_escape(Lang.Plugins[name(x)].Link) ?>"><img src="<?cs
				call:link('icons/' + name(x), '','','','') ?>" alt="<?cs
				var:html_escape('icon: ' + x.Name) ?>" /><br/><?cs
				var:html_escape(Lang.Plugins[name(x)].Link) ?></a></div><?cs
		/if ?><?cs
	/each ?><?cs
/loop ?>

</fieldset>

