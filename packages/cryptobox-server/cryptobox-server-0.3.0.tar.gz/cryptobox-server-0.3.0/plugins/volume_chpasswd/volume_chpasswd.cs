<?cs # $Id$ ?>

<!-- <<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_chpasswd.Title.ChangePassword) ?></<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_chpasswd.Title.ChangePassword) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_chpasswd.Help.Password) ?>

<?cs # show password change form only for encrypted volumes ?>
<?cs if:Data.CurrentDisk.encryption ?>
	<?cs call:print_form_header("set_password", "volume_chpasswd") ?>
	<table>
		<tr>
			<td align="right"><label for="old_pw"><?cs var:html_escape(Lang.Text.EnterCurrentPassword) ?>: </label></td>
			<td><input type="password" name="old_pw" tabindex="20" size="15" id="old_pw" /></td>
			<td></td>
		</tr>
		<tr>
			<td align="right"><label for="new_pw"><?cs var:html_escape(Lang.Text.EnterNewPassword) ?>: </label></td>
			<td><input type="password" name="new_pw" tabindex="21" size="15" id="new_pw" /></td>
			<td></td>
		</tr>
		<tr>
			<td align="right"><label for="new_pw2"><?cs var:html_escape(Lang.Text.EnterSamePassword) ?>: </label></td>
			<td><input type="password" name="new_pw2" tabindex="22" size="15" id="new_pw2" /></td>
			<td>
				<input type="hidden" name="device" value="<?cs var:html_escape(Data.CurrentDisk.device) ?>" />
				<input type="hidden" name="store" value="change_pw" />
				<button type="submit" tabindex="23"><?cs var:html_escape(Lang.Plugins.volume_chpasswd.Button.ChangePassword) ?></button>
			</td>
		</tr>
	</table>
	</form>
<?cs else ?>
	<?cs call:hint("Plugins.volume_chpasswd.FormatForEncryptionSupport") ?>
<?cs /if ?>
</fieldset>

