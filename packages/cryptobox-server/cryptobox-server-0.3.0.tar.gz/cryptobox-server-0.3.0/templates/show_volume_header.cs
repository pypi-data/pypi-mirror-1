<?cs # $Id: show_volume_header.cs 607 2006-12-13 10:01:58Z lars $ ?>

<table class="volume_name"><tr><td>
	<a class="disk_symbol "href="<?cs
		call:link("volume_mount","device",Data.CurrentDisk.device,"","")
		?>"><?cs call:show_volume_icon(Data.CurrentDisk) ?></a>
</td><td>
	<h1 id="volume_name"><?cs var:html_escape(Lang.Title.Volume) ?> <i><?cs
		var:html_escape(Data.CurrentDisk.name) ?></i></h1>
</td></tr></table>


<table id="volume_area">
	<tr>
		<td>&nbsp;</td>
		<?cs include:Settings.TemplateDir + '/volume_plugins.cs' ?>
	</tr>
</table>

<div id="volume_content">

<?cs # this is a little bit dirty: every volume plugin must use 'plugin_heading'
	instead of using 'h2' directly - this makes it possible to override this
	value for embedded plugins (see 'volume_properties') ?>
<?cs set:plugin_heading = "h2" ?>

