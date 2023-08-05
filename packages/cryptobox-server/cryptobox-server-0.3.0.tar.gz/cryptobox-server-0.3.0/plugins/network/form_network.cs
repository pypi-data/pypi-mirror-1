<?cs # $Id: form_network.cs 747 2007-02-03 18:24:07Z age $ ?>

<?cs call:handle_messages() ?>

<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.network.Title.IP) ?>
	</legend>
	<?cs call:print_form_header("network_address", "network") ?>
	<?cs call:show_help(Lang.Plugins.network.Help.Network) ?>

	<table>
		<tr><td>
			<?cs var:html_escape(Lang.Plugins.network.Text.IP) ?>:
		</td><td>
		<!-- maybe display the used network interface?
			but users will not really know what this is about
			admins will know anyway, which interface it is (because of the IP)
		<tr><td>
			<?cs var:html_escape(Lang.Plugins.network.Interface) ?>:
		</td><td> 
		</td></tr>
		-->
		<input class="ipnum" type="text" tabindex="1" name="ip1" size="3" id="ip"
			value="<?cs var:Data.Plugins.network.ip.oc1
		?>" />.<input class="ipnum" type="text" tabindex="2" name="ip2" size="3"
			value="<?cs var:Data.Plugins.network.ip.oc2
		?>" />.<input class="ipnum" type="text" tabindex="3" name="ip3" size="3"
			value="<?cs var:Data.Plugins.network.ip.oc3
		?>" />.<input class="ipnum" type="text" tabindex="4" name="ip4" size="3"
			value="<?cs var:Data.Plugins.network.ip.oc4 ?>" />
		</td></tr>
		<tr><td>
		<?cs var:html_escape(Lang.Plugins.network.Text.NM) ?>:
		</td><td>
		<input class="ipnum" type="text" tabindex="5" name="nm1" size="3" id="nm"
			value="<?cs var:Data.Plugins.network.nm.oc1
		?>" />.<input class="ipnum" type="text" tabindex="6" name="nm2" size="3"
			value="<?cs var:Data.Plugins.network.nm.oc2
		?>" />.<input class="ipnum" type="text" tabindex="7" name="nm3" size="3"
			value="<?cs var:Data.Plugins.network.nm.oc3
		?>" />.<input class="ipnum" type="text" tabindex="8" name="nm4" size="3"
			value="<?cs var:Data.Plugins.network.nm.oc4 ?>" />
		</td></tr><tr><td>
	</table>
	<p>
		<input type="hidden" name="store" value="set_ip" />
		<button type="submit" tabindex="9"><?cs
			var:html_escape(Lang.Plugins.network.Button.Network) ?></button>
	</p>
	</form>
</fieldset>


<fieldset>
	<legend>
		<?cs call:show_plugin_icon() ?>
		<?cs var:html_escape(Lang.Plugins.network.Title.GW) ?>
	<?cs call:print_form_header("network_gateway", "network") ?>
	<?cs call:show_help(Lang.Plugins.network.Help.Gateway) ?>

	<table>	
		<tr><td>
		<?cs var:html_escape(Lang.Plugins.network.Text.GW) ?>:
		</td><td>
		<input class="ipnum" type="text" tabindex="20" name="ip1" size="3" id="ip"
			value="<?cs var:Data.Plugins.network.gw.oc1
		?>" />.<input class="ipnum" type="text" tabindex="21" name="ip2" size="3"
			value="<?cs var:Data.Plugins.network.gw.oc2
		?>" />.<input class="ipnum" type="text" tabindex="22" name="ip3" size="3"
			value="<?cs var:Data.Plugins.network.gw.oc3
		?>" />.<input class="ipnum" type="text" tabindex="23" name="ip4" size="3"
			value="<?cs var:Data.Plugins.network.gw.oc4 ?>" />
		</td></tr>
	</table>
	<p>
		<input type="hidden" name="store" value="set_gateway" />
		<button type="submit" tabindex="24"><?cs
			var:html_escape(Lang.Plugins.network.Button.Gateway) ?></button>
	</p>
	</form>

	<!-- DHCP comes later
	<?cs call:show_help(Lang.Plugins.network.Help.DHCP) ?>
	<p>
		<input type="checkbox" name="dhcp" value="1" id="dhcp" /><label for="dhcp"><?cs var:html_escape(Lang.Plugins.network.Text.DHCP) ?></label>
	</p>
	-->
	
</fieldset>

