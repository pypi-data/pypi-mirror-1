<?cs loop: x = #0, subcount(Data.Plugins.partition.Parts)-1, #1 ?>
	<input type="hidden" name="part<?cs var:x ?>_size" value="<?cs var:Data.Plugins.partition.Parts[x].Size ?>" />
	<input type="hidden" name="part<?cs var:x ?>_type" value="<?cs var:Data.Plugins.partition.Parts[x].Type ?>" /><?cs
/loop ?>

<input type="hidden" name="block_device" value="<?cs var:html_escape(Data.Plugins.partition.Device) ?>" />

<?cs if:Data.Plugins.partition.CreateConfigPartition ?>
	<input type="hidden" name="create_config_partition" value="1" />
<?cs /if ?>

<?cs # the confirm question was asked only once ?>
<input type="hidden" name="confirm" value="1" />

