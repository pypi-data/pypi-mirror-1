<!-- <<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_mount.Title.Umount) ?></<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_mount.Title.Umount) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_mount.Help.Close) ?>

<?cs call:print_form_header("umount", "volume_mount") ?>
	<table><tr><td>
		<input type="hidden" name="device" value="<?cs var:html_escape(Data.CurrentDisk.device) ?>" />
	   <input type="hidden" name="action" value="umount" />
	<button type="submit"><?cs var:html_escape(Lang.Plugins.volume_mount.Button.Umount) ?></button>
	</td></tr></table>
</form>
</fieldset>

