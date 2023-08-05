<?cs # $Id: plugin_list.cs 790 2007-02-08 02:16:41Z lars $ ?>

<?cs call:handle_messages() ?>

<?cs call:show_help(Lang.Plugins.plugin_manager.Help.PluginManager) ?>

<?cs # just as a sidenote: we add the strange 'x' argument below to prevent the browser
	from thinking, that it can use the cached page again, if a user calls the "down" or
	"up" action twice for the same plugin ?>

<?cs # <form> starts here ?>
<?cs call:print_form_header("manage_plugins", "plugin_manager") ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.plugin_manager.Title.VolumePlugins) ?>
	</legend>
	<?cs call:show_help(Lang.Plugins.plugin_manager.Help.VolumePlugins) ?>

	<table class="plugin_list" id="volume_plugins"><?cs
			# 'id' is used as a link anchor ?>
		<tr>
			<th width="40%"></th>
			<th colspan="2"><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.WhereVisible) ?></th>
			<th></th>
			<th></th>
			<th></th>
		</tr>
		<tr>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.PluginName) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.InVolumeRegister) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.InVolumeProperties) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.RequestsAuth) ?></th>
			<th colspan="2"><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.PluginRank) ?></th>
		</tr>
		<?cs # count volume plugins ?><?cs set: all_count = #0
		?><?cs each:x = Settings.PluginList ?><?cs if: x.Types.volume ?><?cs
			set: all_count = all_count + 1 ?><?cs /if ?><?cs /each ?>
		<?cs set:run_counter = 0 ?><?cs
		loop: index = #0, #100, #1 ?><?cs
		each:x = Settings.PluginList ?><?cs if:(x.Rank == index) && x.Types.volume
		?><?cs set: run_counter = run_counter + 1 ?>
		<tr>
			<td style="text-align:left" id="plugin_anchor_<?cs var:html_escape(name(x))
					?>"><img src="<?cs call:link("icons/" + name(x), "", "", "", "")
					?>" alt="" class="logo" />&nbsp;<?cs
					var:html_escape(Lang.Plugins[name(x)].Name) ?></td>
			<td><input type="checkbox" name="<?cs var:name(x) ?>_visible_volume" <?cs if:x.Visible.volume ?>checked="checked"<?cs /if ?> /></td>
			<td><input type="checkbox" name="<?cs var:name(x) ?>_visible_properties" <?cs if:x.Visible.properties ?>checked="checked"<?cs /if ?> /></td>
			<td><input type="checkbox" name="<?cs var:name(x) ?>_auth" <?cs if:x.RequestAuth ?>checked="checked"<?cs /if ?> /></td>
			<td class="down">
				<?cs if:run_counter != all_count ?><a href="<?cs
					call:link("plugin_manager", "plugin_name", name(x), "action", "down")
					?>&amp;x=<?cs var:run_counter ?>#volume_plugins"><img class="arrow"
					src="icons/plugin_manager?image=tango-go-down.png" alt="<?cs
					var:html_escape(Lang.Plugins.plugin_manager.Button.Down) ?>" 
					title="<?cs var:html_escape(Lang.Plugins.plugin_manager.Button.Down) 
					?>" /></a><?cs /if ?>
			</td>
			<td class="up">
				<?cs if:run_counter != 1 ?><a href="<?cs
					call:link("plugin_manager", "plugin_name", name(x), "action", "up")
					?>&amp;x=<?cs var:run_counter ?>#volume_plugins" ><img
					src="icons/plugin_manager?image=tango-go-up.png" alt="<?cs
					var:html_escape(Lang.Plugins.plugin_manager.Button.Up) ?>"
					title="<?cs var:html_escape(Lang.Plugins.plugin_manager.Button.Up)
					?>" /></a><?cs /if ?>
				<input type="hidden" name="<?cs var:html_escape(name(x))
					?>_rank" value="<?cs var:html_escape(x.Rank) ?>" />
				<input type="hidden" name="<?cs var:name(x) ?>_listed" value="1" /></td>
		</tr><?cs /if ?><?cs /each ?><?cs /loop ?>
	</table>
</fieldset>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.plugin_manager.Title.SystemPlugins) ?>
	</legend>
	<?cs call:show_help(Lang.Plugins.plugin_manager.Help.SystemPlugins) ?>
	<table class="plugin_list" id="system_plugins"><?cs
			# 'id' is used as a link anchor ?>
		<tr>
			<th width="40%"></th>
			<th colspan="2"><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.WhereVisible) ?></th>
			<th></th>
			<th></th>
			<th></th>
		</tr>
	<?cs # count system plugins ?><?cs set: all_count = #0
		?><?cs each:x = Settings.PluginList ?><?cs if: x.Types.system ?><?cs
			set: all_count = all_count + 1 ?><?cs /if ?><?cs /each ?>
		<tr>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.PluginName) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.InMenu) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.InPreferences) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.RequestsAuth) ?></th>
			<th colspan="2"><?cs var:html_escape(Lang.Plugins.plugin_manager.Text.PluginRank) ?></th>
		</tr>
	<?cs set:run_counter = 0 ?><?cs
	loop:index = #0, #100, #1 ?><?cs
	each:x = Settings.PluginList ?><?cs if:(x.Rank == index) && x.Types.system
		?><?cs set: run_counter = run_counter + 1 ?><tr>
			<td style="text-align:left" id="plugin_anchor_<?cs var:html_escape(name(x))
					?>"><img src="<?cs call:link("icons/" + name(x), "", "", "", "")
					?>" alt="" class="logo" />&nbsp;<?cs
					var:html_escape(Lang.Plugins[name(x)].Name) ?></td>
			<td><input type="checkbox" name="<?cs var:name(x) ?>_visible_menu" <?cs if:x.Visible.menu ?>checked="checked"<?cs /if ?> /></td>
			<td><input type="checkbox" name="<?cs var:name(x) ?>_visible_preferences" <?cs if:x.Visible.preferences ?>checked="checked"<?cs /if ?> /></td>
			<td><input type="checkbox" name="<?cs var:name(x) ?>_auth" <?cs if:x.RequestAuth ?>checked="checked"<?cs /if ?> /></td>
			<td class="down">
				<?cs if:run_counter != all_count ?><a href="<?cs
					call:link("plugin_manager", "plugin_name", name(x), "action", "down")
					?>&amp;x=<?cs var:run_counter ?>#system_plugins"><img
					src="icons/plugin_manager?image=tango-go-down.png" alt="<?cs
					var:html_escape(Lang.Plugins.plugin_manager.Button.Down) ?>"
					title="<?cs var:html_escape(Lang.Plugins.plugin_manager.Button.Down)
					?>" /></a><?cs /if ?>
			<td class="up">
				<?cs if:run_counter != 1 ?><a href="<?cs
					call:link("plugin_manager", "plugin_name", name(x), "action", "up")
					?>&amp;x=<?cs var:run_counter ?>#system_plugins" ><img
					src="icons/plugin_manager?image=tango-go-up.png" alt="<?cs
					var:html_escape(Lang.Plugins.plugin_manager.Button.Up) ?>"
					title="<?cs var:html_escape(Lang.Plugins.plugin_manager.Button.Up)
					?>" /></a><?cs /if ?>
				<input type="hidden" name="<?cs var:html_escape(name(x))
					?>_rank" value="<?cs var:html_escape(x.Rank) ?>" />
				<input type="hidden" name="<?cs var:name(x) ?>_listed" value="1" /></td>
		</tr><?cs /if ?><?cs /each ?><?cs /loop ?>
	</table>

</fieldset>

<p>
	<input type="hidden" name="store" value="1" />
	<button type="submit"><?cs var:html_escape(Lang.Plugins.plugin_manager.Button.SaveSettings) ?></button>
</p>

</form>

