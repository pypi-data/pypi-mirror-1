<!-- <?cs # $Id: volume_format_luks.cs 717 2007-01-26 22:23:02Z age $ ?>

	<<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_format_fs.Title.Format) ?></<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_format_fs.Title.Format) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_format_fs.Help.LuksFormat) ?>


<?cs if:Data.CurrentDisk.active ?>
	<?cs call:hint("Plugins.volume_format_fs.UnmountBeforeInit") ?>
<?cs else ?>

	<?cs call:hint("Plugins.volume_format_fs.FormatWarning") ?>

	<?cs call:print_form_header("set_luks", "volume_format_fs") ?>
		<p><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.FSType) ?>: <?cs var:html_escape(Data.Plugins.volume_format_fs.fs_type) ?></p>
		<p><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.IsEncrypted) ?>: <?cs if:Data.Plugins.volume_format_fs.container_type == "luks" ?><?cs
			var:html_escape(Lang.Plugins.volume_format_fs.Text.Yes) ?><?cs else ?><?cs
			var:html_escape(Lang.Plugins.volume_format_fs.Text.No) ?><?cs /if ?></p>

		<?cs call:show_help(Lang.Plugins.volume_format_fs.Help.Password) ?>
		<p><label for="crypto_password"><?cs var:html_escape(Lang.Text.EnterNewPassword) ?>: </label> <input type="password" id="crypto_password" name="crypto_password" /></p>
		<p><label for="crypto_password2"><?cs var:html_escape(Lang.Text.EnterSamePassword) ?>: </label> <input type="password" id="crypto_password2" name="crypto_password2" /></p>
		<p><input type="hidden" name="device" value="<?cs var:Data.CurrentDisk.device ?>" />
		<input type="hidden" name="fs_type" value="<?cs var:html_escape(Data.Plugins.volume_format_fs.fs_type) ?>" />
		<input type="hidden" name="container_type" value="<?cs var:html_escape(Data.Plugins.volume_format_fs.container_type) ?>" />
		<input type="hidden" name="store" value="step2" />
		<button type="submit"><?cs var:html_escape(Lang.Plugins.volume_format_fs.Button.Format) ?></button></p>
	</form>

<?cs /if ?>
</fieldset>

