<?cs # $Id: form_shutdown.cs 747 2007-02-03 18:24:07Z age $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.shutdown.Title) ?>
	</legend>

<?cs call:show_help(Lang.Plugins.shutdown.Help.Shutdown) ?>

<div class="plugin_system">
	<a href="<?cs call:link('shutdown','type','shutdown','','') ?>">
	<img src="<?cs call:link('icons/shutdown','image','gnome-shutdown.gif','','')
	?>" alt="icon: shutdown" /><br/><?cs var:html_escape(Lang.Plugins.shutdown.Button.Shutdown) ?></a></div>

<div class="plugin_system">
	<a href="<?cs call:link('shutdown','type','reboot','','') ?>">
	<img src="<?cs call:link('icons/shutdown','image','gnome-reboot.gif','','')
	?>" alt="icon: reboot" /><br/><?cs var:html_escape(Lang.Plugins.shutdown.Button.Reboot) ?></a></div>

</fieldset>
