<?cs # $Id: show_log.cs 808 2007-02-10 00:25:01Z age $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.logs.Title) ?>
	</legend>
<?cs call:show_help(Lang.Plugins.logs.Help.EventLog) ?>

<table border="0" align="center"><tr>
	<td><?cs call:print_form_header("log-all", "logs") ?>
		<button type="submit" value="refresh"><?cs
			var:html_escape(Lang.Plugins.logs.Text.ShowAll) ?></button>
	</form></td>
	<td><?cs call:print_form_header("log-warnings", "logs") ?>
		<input type="hidden" name="level" value="WARNING" />
		<button type="submit" value="refresh"><?cs
			var:html_escape(Lang.Plugins.logs.Text.AtLeastWarnings) ?></button>
	</form></td>
	<td><?cs call:print_form_header("log-only-error", "logs") ?>
		<input type="hidden" name="level" value="ERROR" />
		<button type="submit" value="refresh"><?cs
			var:html_escape(Lang.Plugins.logs.Text.OnlyErrors) ?></button>
	</form></td>
</tr></table>

<div id="log">

	<?cs if:Data.Plugins.logs.Destination != "file" ?>
		<?cs call:hint("Plugins.logs.NoLogFileConfigured") ?>
	<?cs elif:subcount(Data.Plugins.logs.Content) > 0 ?>
		<table class="log"><?cs # the first line dictates if we show meta info or not
			?><?cs if:Data.Plugins.logs.Content.0.Level ?>
				<tr><th></th>
					<th><?cs var:html_escape(Lang.Plugins.logs.Text.AgeOfEvent) ?></th>
					<th><?cs var:html_escape(Lang.Plugins.logs.Text.EventText) ?></th>
				</tr>
				<?cs loop:index = #0, subcount(Data.Plugins.logs.Content)-1, #1 ?><?cs
				with:x=Data.Plugins.logs.Content[index] ?><?cs
				if:x.Text ?><?cs
					if:x.Level == "ERROR" ?><?cs
						set:meta_file="dialog-error_tango.gif" ?><?cs
					elif:x.Level == "WARNING" ?><?cs
						set:meta_file="dialog-warning_tango.gif" ?><?cs
					else ?><?cs
						set:meta_file="dialog-information_tango.gif" ?><?cs
					/if ?>
					<tr><td class="level"><img src="<?cs
						call:link("cryptobox-misc/" + meta_file, "", "", "", "") ?>"
						alt="symbol: <?cs var:html_escape(x.Level) ?>" /></td>
					<td class="time"><?cs if:x.TimeDiff.Value ?><?cs
						var:html_escape(x.TimeDiff.Value) ?>&nbsp;<?cs
						var:html_escape(Lang.Plugins.logs.Text.TimeUnits[
								x.TimeDiff.Unit]) ?><?cs
					/if ?></td>
					<td class="text"><?cs var:html_escape(x.Text) ?></td></tr><?cs
				/if ?><?cs /with ?><?cs /loop ?><?cs
			else ?><?cs
				loop:index = #0, subcount(Data.Plugins.logs.Content)-1, #1 ?><?cs
				with:x=Data.Plugins.logs.Content[index] ?>
					<tr><td><?cs var:html_escape(x.Text) ?></td></tr><?cs
				/with ?><?cs /loop ?><?cs
			/if ?>
		</table>
	<?cs call:print_form_header("download-log", "downloads/logs") ?>
		<p style="text-align:center">	
		<button type="submit" value="refresh"><?cs
			var:html_escape(Lang.Plugins.logs.Text.DownloadLogFile) ?></button>
		</p>
	</form>
	<?cs else ?>
		<p style="text-align:center">	
		<?cs call:hint("Plugins.logs.EmptyLog") ?>
		</p>
	<?cs /if ?>

</div>
</fieldset>

