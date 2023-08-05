<?cs # $Id: set_partitions.cs 835 2007-02-19 01:22:31Z lars $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.partition.Title) ?>
	</legend>

<?cs # show nothing if the harddisk is not partitionable (e.g. still active) ?>
<?cs if:(Data.Plugins.partition.availSize > 0) || (subcount(Data.Plugins.partition.Parts) > 0) ?>

<fieldset>
<legend><?cs var:html_escape(Lang.Plugins.partition.Text.SpecifyPartitions) ?></legend>

<?cs call:show_help(Lang.Plugins.partition.Help.PartitionList) ?>


<div align="center"><?cs call:print_form_header("part_del_" + x, "partition") ?>
	<?cs include:Data.Plugins.partition.PluginDir +
			"/current_partition_info.cs" ?>

	<table class="partition">
		<tr>
			<th><?cs var:html_escape(Lang.Plugins.partition.Text.PartNum) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.partition.Text.Size) ?></th>
			<th><?cs var:html_escape(Lang.Plugins.partition.Text.PartType) ?></th>
			<th></th>
		</tr>

		<?cs loop: x = #0, subcount(Data.Plugins.partition.Parts)-1, #1 ?>
		<tr>
			<td><?cs var:x ?></td>
			<td><?cs var:Data.Plugins.partition.Parts[x].Size ?></td>
			<td><?cs var:Data.Plugins.partition.Parts[x].Type ?></td>
			<td>
				<input class="button" type="submit" name="del_part_<?cs var:x ?>"
					value="<?cs var:html_escape(Lang.Plugins.partition.Button.DelPartition) ?>" />
			</td>
		</tr>
		<?cs /loop ?>

		<?cs # new partition input if space is available ?>
		<?cs if:Data.Plugins.partition.availSize > 0 ?>
		<tr>
			<?cs set: x = subcount(Data.Plugins.partition.Parts) ?>
			<td><?cs var:x ?></td>
			<td><input type="text" name="part<?cs var:x ?>_size" size="8" value="<?cs var:Data.Plugins.partition.availSize ?>" tabindex="1" /></td>
			<td><select name="part<?cs var:x ?>_type" tabindex="2" size="0"><?cs each: t = Data.Plugins.partition.Types ?><option <?cs if:t == "windows" ?>selected="selected"<?cs /if ?>><?cs var:t ?></option>
				<?cs /each ?></select></td>
			<td>
				<input type="hidden" name="part<?cs var:x ?>_unconfirmed" value="1" />
				<input class="button" type="submit" name="add_part" value="<?cs
					var:html_escape(Lang.Plugins.partition.Button.AddPartition) ?>" />
			</td>
		</tr>
		<?cs /if ?>
	</table>
</form></div>

<?cs if:Data.Plugins.partition.CreateConfigPartition ?>
	<?cs call:show_help(Lang.Plugins.partition.Help.ConfigPartition) ?>
	<p><?cs var:html_escape(Lang.Plugins.partition.Text.CreateConfigPartition) ?></p>
<?cs /if ?>

</fieldset>


<?cs if:subcount(Data.Plugins.partition.ExistingContainers) ?>
	<fieldset>
	<legend><?cs var:html_escape(Lang.Plugins.partition.Text.RemovalContainers) ?></legend>
		<?cs call:show_help(Lang.Plugins.partition.Help.RemoveExistingContainers) ?>
		<?cs each:item = Data.Plugins.partition.ExistingContainers ?><?cs
			each:one_container = Data.Disks ?><?cs
				if:item == one_container.device ?><?cs
					call:show_volume(one_container) ?><?cs
				/if ?><?cs
			/each ?><?cs
		/each ?>
	</fieldset>
<?cs /if ?>

<?cs if:subcount(Data.Plugins.partition.Parts) > 0 ?>
	<?cs call:hint("Plugins.partition.DeviceDataIsLost") ?>

	<table align="center"><tr><td>
	<?cs call:print_form_header("part_finish", "partition") ?>
		<?cs include:Data.Plugins.partition.PluginDir +
				"/current_partition_info.cs" ?>
		<input class="button" type="submit" name="finish" value="<?cs
				var:html_escape(Lang.Plugins.partition.Button.SavePartitions) ?>" />
			</td>
		<td><input class="button" type="submit" name="cancel" value="<?cs
				var:html_escape(Lang.Plugins.partition.Button.AbortPartitions) ?>" />
			</td>
		</tr></table>
<?cs /if ?>

<?cs /if ?>

</fieldset>

