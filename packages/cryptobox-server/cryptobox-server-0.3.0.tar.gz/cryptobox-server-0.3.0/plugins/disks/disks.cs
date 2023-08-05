<?cs # $Id: disks.cs 747 2007-02-03 18:24:07Z age $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.disks.Title) ?>
	</legend>
<?cs if:subcount(Data.Disks) == 0 ?>
	<?cs call:hint("Plugins.disks.NoDisksAvailable") ?>
<?cs else ?>
	<?cs # we use "loop" instead of "each" to keep the order of the disks ?>
	<?cs loop: index = #0, subcount(Data.Disks)-1, #1 ?>
		<?cs call:show_volume(Data.Disks[index]) ?>
	<?cs /loop ?>
<?cs /if ?>
</fieldset>

