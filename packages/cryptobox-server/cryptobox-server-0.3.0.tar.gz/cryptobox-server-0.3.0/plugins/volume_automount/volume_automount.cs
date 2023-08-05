<!-- <?cs # $Id: volume_automount.cs 715 2007-01-26 09:44:00Z age $ ?>

<<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_automount.Title.AutoMountVolume) ?></<?cs var:plugin_heading ?>>
-->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_automount.Title.AutoMountVolume) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_automount.Help.AutoMount) ?>

<?cs if:!Data.CurrentDisk.encryption ?>
	<?cs call:print_form_header("automount", "volume_automount") ?>
		<p><input type="hidden" name="device" value="<?cs var:html_escape(Data.CurrentDisk.device) ?>" />
		<?cs if:Data.Plugins.volume_automount.automount_setting ?>
			<?cs var:html_escape(Lang.Plugins.volume_automount.Text.AutoIsOn) ?><br/>
			<input type="hidden" name="action" value="disable" />
			<button type="submit"><?cs var:html_escape(Lang.Plugins.volume_automount.Button.AutoMountOff) ?></button>
		<?cs else ?>
			<?cs var:html_escape(Lang.Plugins.volume_automount.Text.AutoIsOff) ?>
			<input type="hidden" name="action" value="enable" />
			<button type="submit"><?cs var:html_escape(Lang.Plugins.volume_automount.Button.AutoMountOn) ?></button>
		<?cs /if ?></p>
	</form>
<?cs else ?>
	<?cs call:hint("Plugins.volume_automount.NoAutoMountForEncryptedVolumes") ?>
<?cs /if ?>
</fieldset>

