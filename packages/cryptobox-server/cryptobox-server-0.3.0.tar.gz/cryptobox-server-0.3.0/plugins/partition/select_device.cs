<?cs # $Id: select_device.cs 835 2007-02-19 01:22:31Z lars $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.partition.Title) ?>
	</legend>

<?cs call:show_help(Lang.Plugins.partition.Help.Partitioning) ?>

<?cs if:subcount(Data.Plugins.partition.BlockDevices) > 0 ?>

	<?cs call:print_form_header("select_device", "partition") ?>

		<?cs call:hint("Plugins.partition.DeviceDataIsLost") ?>

		<?cs call:show_help(Lang.Plugins.partition.Help.SelectDevice) ?>

		<p><label for="block_device"><?cs var:html_escape(Lang.Plugins.partition.Text.SelectDevice) ?>: </label><br/>
		<select name="block_device" id="block_device" tabindex="1" size="0">
			<?cs each:x = Data.Plugins.partition.BlockDevices
				?><option value="<?cs var:html_escape(x.name) ?>"><?cs
					var:html_escape(x.name) ?> (<?cs var:html_escape(x.size) ?>)</option>
				<?cs /each ?>
		</select></p>

		<p><input type="checkbox" name="confirm" value="1" id="confirm" /><label for="confirm"><?cs var:html_escape(Lang.Plugins.partition.Text.Confirm) ?></label></p>

		<p><input type="hidden" name="device" value="<?cs var:Data.CurrentDisk.device ?>" />
		<?cs call:show_help(Lang.Plugins.partition.Help.PartMode) ?>

		<div align="center"><table><tr>
			<!-- we have to avoid an ugly IE bug, that ignores the "value" attribute
				of "button" elements: if a variable called 'easy' is set, then this
				button was choosen - uuuuuugly! -->
			<td><input class="button" type="submit" name="easy" value="<?cs var:html_escape(Lang.Plugins.partition.Button.EasySetup) ?>" /></td>
			<td><input class="button" type="submit" name="add_part" value="<?cs var:html_escape(Lang.Plugins.partition.Button.SelectDevice) ?>" /></td>
		</tr></table></div>

	</form>

<?cs /if ?>

</fieldset>

<?cs # a warning will be displayed if there are no disks available ?>

