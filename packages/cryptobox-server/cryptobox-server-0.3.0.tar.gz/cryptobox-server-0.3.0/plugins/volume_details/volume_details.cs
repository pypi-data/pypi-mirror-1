<!-- <?cs # $Id: volume_details.cs 717 2007-01-26 22:23:02Z age $ ?>
<<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_details.Title.Details) ?></<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_details.Title.Details) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_details.Help.Details) ?>

<ul>
	<li><?cs var:html_escape(Lang.Text.ContainerName) ?>: <?cs var:html_escape(Data.CurrentDisk.name) ?></li>
	<li><?cs var:html_escape(Lang.Plugins.volume_details.Text.DeviceName) ?>: <?cs var:html_escape(Data.CurrentDisk.device) ?></li>
	<li><?cs var:html_escape(Lang.Plugins.volume_details.Text.Status) ?>: <?cs if:Data.CurrentDisk.active ?><?cs var:html_escape(Lang.Plugins.volume_details.Text.StatusActive) ?><?cs else ?><?cs var:html_escape(Lang.Plugins.volume_details.Text.StatusPassive) ?><?cs /if ?></li>
	<li><?cs var:html_escape(Lang.Plugins.volume_details.Text.EncryptionStatus) ?>: <?cs if:Data.CurrentDisk.encryption ?><?cs var:html_escape(Lang.Plugins.volume_details.Text.Yes) ?><?cs else ?><?cs var:html_escape(Lang.Plugins.volume_details.Text.No) ?><?cs /if ?></li>
	<?cs if:Data.CurrentDisk.active ?>
		<li><?cs var:html_escape(Lang.Plugins.volume_details.Text.Size.All) ?>: <?cs var:html_escape(Data.CurrentDisk.capacity.size) ?> MB</li>
		<li><?cs var:html_escape(Lang.Plugins.volume_details.Text.Size.Avail) ?>: <?cs var:html_escape(Data.CurrentDisk.capacity.free) ?> MB</li>
		<li><?cs var:html_escape(Lang.Plugins.volume_details.Text.Size.Used) ?>: <?cs var:html_escape(Data.CurrentDisk.capacity.percent) ?>%</li>
	<?cs /if ?>
</ul>

</fieldset>

