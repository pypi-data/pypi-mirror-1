<?cs # $Id: volume_properties.cs 715 2007-01-26 09:44:00Z age $ ?>

<!-- <h2><?cs var:html_escape(Lang.Plugins.volume_props.Title.Properties) ?></h2> -->

<?cs call:handle_messages() ?>

<?cs set:plugin_heading = "legend" ?>

<?cs if:Data.Plugins.volume_props.includePlugins ?>
	<?cs # we use 'evar', as we expect 'include' commands inside the variable ?>
	<?cs evar:Data.Plugins.volume_props.includePlugins ?>
<?cs else ?>
	<?cs call:hint("Plugins.volume_props.NoPropertyPlugins") ?>
<?cs /if ?>

