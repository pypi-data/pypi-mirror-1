<?cs # $Id: volume_plugins.cs 629 2006-12-19 23:15:27Z lars $ ?>

<?cs # show all available volume plugins on top of the volume table ?>

<?cs # count volume plugins ?>
<?cs set:volume_plugin_count=0 ?><?cs
  each: x = Settings.PluginList ?><?cs
	if:x.Types.volume ?><?cs set:volume_plugin_count=volume_plugin_count+1 ?><?cs /if ?><?cs
	/each ?>

<?cs # show one tab for each plugin ?>
<?cs if:volume_plugin_count > 0 ?>
	<?cs # two possibilities to find the active ('to be marked') plugin:
			- the active plugin is part of the volume menu list -> mark it
			- the rest: mark 'volume_props' ?><?cs
	# first: set default value ?><?cs
	set:markPlugin = 'volume_props' ?><?cs
	# check if the active plugin is visible in the menu ?><?cs
	each:plugin = Settings.PluginList ?><?cs
		if:plugin.Visible.volume && (name(plugin) == Data.ActivePlugin) ?><?cs
			set:markPlugin = name(plugin) ?><?cs
		/if ?><?cs
	/each ?><?cs
	# sort the Plugins - using the most stupid way :) ?><?cs
	loop: order = #0, #100, #1
		?><?cs # plugins ?><?cs each:x = Settings.PluginList
			?><?cs if:x.Types.volume && x.Visible.volume && x.Rank == order ?>
				<td <?cs if:markPlugin == name(x)
						?>class="volume_plugin_active"<?cs
					else ?>class="volume_plugin_passive"<?cs
				/if ?>><a href="<?cs call:link(name(x),'device',Data.CurrentDisk.device,'','')
					?>" title="<?cs var:html_escape(Lang.Plugins[name(x)].Link)
					?>"><img src="<?cs call:link("icons/" + name(x),'','','','')
					?>" alt="icon: <?cs var:html_escape(name(x)) ?>" />&nbsp;<?cs
					var:html_escape(Lang.Plugins[name(x)].Link)
					?></a></td><!-- add some space --><td>&nbsp;</td><?cs
				/if ?><?cs
		/each ?><?cs
	/loop ?>
<?cs /if ?>

