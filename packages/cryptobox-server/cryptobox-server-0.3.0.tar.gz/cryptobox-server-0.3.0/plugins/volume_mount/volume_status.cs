<?cs if:Data.CurrentDisk.active ?>
	<?cs include:Data.Plugins.volume_mount.PluginDir + "/volume_umount.cs" ?>
<?cs else ?>
	<?cs include:Data.Plugins.volume_mount.PluginDir + "/volume_mount.cs" ?>
<?cs /if ?>

