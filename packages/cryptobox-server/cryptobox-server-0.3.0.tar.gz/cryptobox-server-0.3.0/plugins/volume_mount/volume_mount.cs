<!-- <<?cs var:plugin_heading ?>>
<?cs var:html_escape(Lang.Plugins.volume_mount.Title.Mount) ?> 
</<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>


<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_mount.Title.Mount) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_mount.Help.Open) ?>

<?cs call:print_form_header("mount", "volume_mount") ?>
	<table>
		<tr>
			<td>
				<input type="hidden" name="device" value="<?cs var:html_escape(Data.CurrentDisk.device) ?>" />
				<?cs if:Data.CurrentDisk.encryption ?>
					<input type="hidden" name="action" value="mount_luks" />
				<?cs else ?>
					<input type="hidden" name="action" value="mount_plain" />
				<?cs /if ?>
			</td>
			<?cs if:Data.CurrentDisk.encryption ?>
			<td>
				<label for="pw"><?cs var:html_escape(Lang.Plugins.volume_mount.Text.EnterCurrentPassword) ?>: </label>
			</td><td>	
				<input type="password" id="pw" name="pw" size="20" maxlength="60" />
			</td>
			<?cs /if ?>
			<td>
				<button type="submit"><?cs var:html_escape(Lang.Plugins.volume_mount.Button.Mount) ?></button>
			</td>
		</tr>
	</table>
</form>
</fieldset>

