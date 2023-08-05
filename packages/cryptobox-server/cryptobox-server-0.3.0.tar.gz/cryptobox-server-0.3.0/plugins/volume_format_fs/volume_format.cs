<!-- <<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_format_fs.Title.Format) ?></<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_format_fs.Title.Format) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_format_fs.Help.Format) ?>

<?cs if:Data.CurrentDisk.active ?>
	<?cs call:hint("Plugins.volume_format_fs.UnmountBeforeInit") ?>
<?cs else ?>

	<?cs call:hint("Plugins.volume_format_fs.FormatWarning") ?>

	<?cs call:print_form_header("set_type", "volume_format_fs") ?>
	<table border="0">
	<tr>
	</tr><tr>
		<td>
			<label for="fs_type"><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.FSType)
			?>: </label>
		</td>
		<td>
			<select name="fs_type" id="fs_type" size="0">
				<?cs each:x = Data.Plugins.volume_format_fs.fs_types ?>
					<option <?cs if:x == "windows" ?>selected="selected"<?cs /if ?>><?cs var:html_escape(x) ?></option><?cs /each ?>
				</select>
		</td>
		<td><?cs call:show_help(Lang.Plugins.volume_format_fs.Help.Filesystem) ?></td>
	</tr>
	<tr>
	</tr><tr>
		<td>
			<p><label for="container_type"><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.IsEncrypted)
		?>: </label>
		</td>
		<td>
			<select name="container_type" id="container_type">
			<option value="luks" <?cs if:Data.Plugins.volume_format_fs.container_type != "plain" ?>selected="selected"<?cs /if ?>><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.Yes) ?></option>
			<option value="plain" <?cs if:Data.Plugins.volume_format_fs.container_type == "plain" ?>selected="selected"<?cs /if ?>><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.No) ?></option>
			</select>
		</td>
		<td><?cs call:show_help(Lang.Plugins.volume_format_fs.Help.Encryption) ?></td>
	</tr><tr>
		<td colspan="2">
			<input type="checkbox" name="confirm" value="1" id="confirm" /><label for="confirm"><?cs var:html_escape(Lang.Plugins.volume_format_fs.Text.Confirm) ?></label>
			<input type="hidden" name="device" value="<?cs var:Data.CurrentDisk.device ?>" />
			<input type="hidden" name="store" value="step1" />
		</td>
		<td><?cs call:show_help(Lang.Plugins.volume_format_fs.Help.Confirm) ?></td>
	</tr><tr>
		<td colspan="3">	
			<button type="submit"><?cs var:html_escape(Lang.Plugins.volume_format_fs.Button.Format) ?></button>
		</td>
	</tr>
	</form>
	</table>

<?cs /if ?>
</fieldset>

