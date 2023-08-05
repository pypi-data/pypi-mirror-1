<!-- <?cs # $Id$ ?> <<?cs var:plugin_heading ?>><?cs var:html_escape(Lang.Plugins.volume_rename.Title.ChangeVolumeName) ?></<?cs var:plugin_heading ?>> -->

<?cs call:handle_messages() ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.volume_rename.Title.ChangeVolumeName) ?> </legend>

<?cs call:show_help(Lang.Plugins.volume_rename.Help.Rename) ?>

<?cs if:Data.CurrentDisk.active ?>
	<?cs call:hint("Plugins.volume_rename.NoRenameIfActive") ?>
<?cs else ?>
	<?cs call:print_form_header("set_name", "volume_rename") ?>
		<table>
			<tr>
				<td>
					<label for="vol_name"><?cs var:html_escape(Lang.Text.ContainerName) ?>: </label>
				<input type="text" name="vol_name" tabindex="10" size="15" id="vol_name" value="<?cs var:html_escape(Data.CurrentDisk.name) ?>" />
				</td>
				<td>
					<input type="hidden" name="device" value="<?cs var:html_escape(Data.CurrentDisk.device) ?>" />
					<input type="hidden" name="store" value="set_name" />
				</td>
				<td>
					<button type="submit" tabindex="11"><?cs var:html_escape(Lang.Plugins.volume_rename.Button.ContainerNameSet) ?></button>
				</td>
			</tr>
		</table>
	</form>
<?cs /if ?>
</fieldset>

