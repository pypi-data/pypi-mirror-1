<?cs # $Id: form_date.cs 790 2007-02-08 02:16:41Z lars $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.date.Title) ?>
	</legend>

<?cs call:show_help(Lang.Plugins.date.Help.ChangeDate) ?>

<?cs call:print_form_header("set_date", "date") ?>

	<p><label for="date"><?cs var:html_escape(Lang.Plugins.date.Text.Date) ?>: </label><br/>
		<select id="date" name="day" tabindex="1" size="0"><?cs
			loop: x = #1, #31, #1 ?>
				<?cs if:x == Data.Plugins.date.day ?><option selected="selected"><?cs
					else ?><option><?cs /if ?><?cs var:x ?></option><?cs /loop ?>
		</select>
		<select name="month" tabindex="2" size="0"><?cs
			loop: x = #1, #12, #1 ?>
				<?cs if:x == Data.Plugins.date.month ?><option selected="selected" <?cs
					else ?><option <?cs /if ?>value="<?cs var:x ?>"><?cs
					var:html_escape(Lang.Plugins.date.Text.Months[x]) ?></option><?cs /loop ?>
		</select>
		<select name="year" tabindex="3" size="0"><?cs
			loop: x = #2006, #2025, #1 ?>
				<?cs if:x == Data.Plugins.date.year ?><option selected="selected"><?cs
					else ?><option><?cs /if ?><?cs var:x ?></option><?cs /loop ?>
		</select></p>

	<p><label for="time"><?cs var:html_escape(Lang.Plugins.date.Text.Time) ?>: </label><br/>
		<select id="time" name="hour" tabindex="4" size="0"><?cs
			loop: x = #0, #23, #1 ?>
				<?cs if:x == Data.Plugins.date.hour ?><option selected="selected"><?cs
					else ?><option><?cs /if ?><?cs if:x<10 ?>0<?cs /if ?><?cs var:x ?></option><?cs /loop ?>
		</select>&nbsp;:&nbsp;
		<select name="minute" tabindex="5" size="0"><?cs
			loop: x = #0, #59, #1 ?>
				<?cs if:x == Data.Plugins.date.minute ?><option selected="selected"><?cs
					else ?><option><?cs /if ?><?cs if:x<10 ?>0<?cs /if ?><?cs var:x ?></option><?cs /loop ?>
		</select></p>
	
	<p><input type="hidden" name="store" value="yes" />

	<button type="submit" tabindex="6"><?cs var:html_escape(Lang.Plugins.date.Button.ConfigDate) ?></button></p>

</form>
</fieldset>

