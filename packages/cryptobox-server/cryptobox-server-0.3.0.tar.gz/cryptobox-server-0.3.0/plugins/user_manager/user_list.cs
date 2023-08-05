<?cs # $Id: user_list.cs 777 2007-02-06 02:11:15Z age $ ?>

<?cs call:handle_messages() ?>
<?cs call:show_help(Lang.Plugins.user_manager.Help.UserManagement) ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.user_manager.Title.AddUser) ?>
	</legend>
	<?cs call:show_help(Lang.Plugins.user_manager.Help.AddUser) ?>
	<?cs call:print_form_header("add_user", "user_manager") ?>
	<table class="user_manager">
		<tr><td class="left_column">
			<label for="new_user"><?cs var:html_escape(Lang.Plugins.user_manager.Text.NewUser) ?>:</label></td>
			<td><input id="new_user" type="text" name="user" size="12" /></td>
			<td></td></tr>
		<tr><td class="left_column">
			<label for="new_pw"><?cs var:html_escape(Lang.Text.EnterNewPassword) ?>:</label></td>
			<td><input id="new_pw" type="password" name="new_pw" size="12" /></td>
			<td></td></tr>
		<tr><td class="left_column">
			<label for="new_pw2"><?cs var:html_escape(Lang.Text.EnterSamePassword) ?>:</label></td>
			<td><input id="new_pw2" type="password" name="new_pw2" size="12" /></td>
			<td>
				<input type="hidden" name="store" value="add_user" />
				<button type="submit"><?cs var:html_escape(Lang.Plugins.user_manager.Button.AddUser) ?></button></td></tr>
	</table>
	</form>
</fieldset>


<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.user_manager.Title.ChangePassword) ?>
	</legend>
	<?cs call:show_help(Lang.Plugins.user_manager.Help.ChangePassword) ?>
	<?cs call:print_form_header("change_password", "user_manager") ?>
	<table class="user_manager">
		<tr><td class="left_column">
			<label for="chpw_user"><?cs var:html_escape(Lang.Plugins.user_manager.Text.ChangePasswordUser) ?>:</label></td>
			<td style="text-align:left"><select id="user" name="user" size="0">
					<?cs each:x=Data.Plugins.user_manager.Users ?>
						<option><?cs var:html_escape(x) ?></option>
					<?cs /each ?></select></td>
			<td></td></tr>
		<tr><td class="left_column">
			<label for="ch_pw"><?cs var:html_escape(Lang.Text.EnterNewPassword) ?>:</label></td>
			<td><input id="ch_pw" type="password" name="new_pw" size="12" /></td>
			<td></td></tr>
		<tr><td class="left_column">
			<label for="ch_pw2"><?cs var:html_escape(Lang.Text.EnterSamePassword) ?>:</label></td>
			<td><input id="ch_pw2" type="password" name="new_pw2" size="12" /></td>
			<td>
				<input type="hidden" name="store" value="change_password" />
				<button type="submit"><?cs var:html_escape(Lang.Plugins.user_manager.Button.ChangePassword) ?></button></td></tr>
	</table>
	</form>
</fieldset>


<?cs if:subcount(Data.Plugins.user_manager.Users) > 1 ?>
<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.user_manager.Title.DelUser) ?>
	</legend>
	<?cs call:show_help(Lang.Plugins.user_manager.Help.DelUser) ?>
	<table><tr><td class="left_column">
	<?cs call:print_form_header("del_user", "user_manager") ?>
		<label for="user2del"><?cs var:html_escape(Lang.Plugins.user_manager.Text.DelUser) ?>: </label><select id="user2del" name="user" size="0">
			<?cs each:x=Data.Plugins.user_manager.Users ?><?cs if:x != "admin" ?>
				<option><?cs var:html_escape(x) ?></option>
			<?cs /if ?><?cs /each ?>
		</select>
		<input type="hidden" name="store" value="del_user" />
		<button type="submit"><?cs var:html_escape(Lang.Plugins.user_manager.Button.DelUser) ?></button>
	</form></td></tr></table>
	</fieldset>
<?cs /if ?>

