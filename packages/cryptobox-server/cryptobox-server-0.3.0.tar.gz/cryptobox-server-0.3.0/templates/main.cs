<?cs # $Id: main.cs 799 2007-02-09 19:36:41Z lars $ ?>

<?cs include:Settings.TemplateDir + '/macros.cs' ?>
<?cs include:Settings.TemplateDir + '/header.cs' ?>

<!-- chosen cryptobox template: <?cs var:Settings.TemplateFile ?> -->

<?cs if:Data.ActivePlugin && (Settings.PluginList[Data.ActivePlugin].Types.volume) ?>
	<?cs include:Settings.TemplateDir + '/show_volume_header.cs' ?>
	<?cs include:Settings.TemplateFile ?>
	<?cs include:Settings.TemplateDir + '/show_volume_footer.cs' ?>
<?cs else ?>
	<?cs # enable only, if "system_preferences" is colored, too
			call:show_system_plugin_overview() ?>
	<?cs include:Settings.TemplateFile ?>
<?cs /if ?>


<?cs include:Settings.TemplateDir + '/footer.cs' ?>
