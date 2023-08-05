<?cs # $Id: macros.cs 790 2007-02-08 02:16:41Z lars $ ?><?cs

def:link(path, attr1, value1, attr2, value2)
	?><?cs # first: override previous content of "Temp"
	?><?cs each:attrs = Temp
		?><?cs set:attrs = ""
	?><?cs /each
	?><?cs each:attrs = Settings.LinkAttrs
		?><?cs set:Temp[name(attrs)] = attrs
		?><?cs /each
	?><?cs if:attr1 != "" ?><?cs set:Temp[attr1] = value1 ?><?cs /if
	?><?cs if:attr2 != "" ?><?cs set:Temp[attr2] = value2 ?><?cs /if
	?><?cs var:path
	?><?cs set:first_each = 1
	?><?cs if:subcount(Temp) > 0
		?><?cs each:attrs = Temp
			?><?cs if:(name(attrs) != "") && (attrs != "")
				?><?cs if:first_each == 1 ?><?cs
					set:first_each = 0 ?>?<?cs
				else
					?>&amp;<?cs /if
				?><?cs var:url_escape(name(attrs)) ?>=<?cs var:url_escape(attrs)
			?><?cs /if
		?><?cs /each
	?><?cs elif:path == ""
		?>./<?cs # avoid empty links as they are not standard compliant
	?><?cs /if ?><?cs
 /def ?><?cs


def:show_messageNode(node) ?><?cs
# expects a node of the hdf tree containing a warning/success/environment message
	?><td class="text"><?cs
		if:?node.Title ?><h1><?cs var:html_escape(node.Title) ?></h1><?cs /if ?><?cs
		if:?node.Text ?><?cs var:html_escape(node.Text) ?><?cs /if ?></td><?cs
	if:subcount(node.Link) > 0
		?><td class="link"><a href="<?cs
			if:node.Link.Abs ?><?cs
				var:node.Link.Abs ?><?cs
			elif:node.Link.Prot ?><?cs
				if:?Data.Proxy.ScriptPath ?><?cs
					var:node.Link.Prot + "://" + Data.Proxy.Host + Data.Proxy.ScriptPath + node.Link.Rel ?><?cs
				else ?><?cs
					var:node.Link.Prot + "://" + Data.ScriptURL.Host + Data.ScriptURL.Path + node.Link.Rel ?><?cs
				/if ?><?cs
			else ?><?cs
				call:link(node.Link.Rel, node.Link.Attr1.name, node.Link.Attr1.value, node.Link.Attr2.name, node.Link.Attr2.value) ?><?cs
			/if ?>" title="<?cs var:html_escape(node.Link.Text) ?>"><?cs
				var:html_escape(node.Link.Text) ?></a></td><?cs /if ?><?cs
/def ?><?cs


# the following macro is as ugly as possible - but somehow we have to manage
  to use 'normal' and 'plugin' messages in a clean way:
	- Lang.WarningMessage.???: defined by core functions
	- Lang.Plugins.PLUGINNAME.WarningMessage.???: defined by plugins
  parameters:
    - mname: name of the message (e.g.: "InvalidInput")
	- type: choose one: { warning | success | environment_warning }
	- category: choose one: { WarningMessage | SuccessMessage | EnvironmentWarning }
?><?cs
def:message_dispatch(mname, type, category)
	?><?cs # split the message name into a (potentially existing) plugin-name prefix and the suffix (the python equivalent of the following three lines would be:
		plugPrefix, PlugSuffix = mname[0:mname.find(".",8), mname[mname.find(".",8)+1:]
	?><?cs # initialization ?><?cs set:savedX = 0 ?><?cs
	loop:x = #8, #40, #1 ?><?cs if:(string.slice(mname,x,x+1) == ".") && !savedX ?><?cs set:savedX = x ?><?cs /if ?><?cs /loop
	?><?cs set:plugPrefix = string.slice(mname,0,savedX)
	?><?cs set:plugSuffix = string.slice(mname,savedX+1,string.length(mname))
	?><?cs # choose the appropriate symbol file
	?><?cs if:type == "success" ?><?cs
			set:symbolFile = "dialog-information_tango.gif"
		?><?cs elif:type == "warning" ?><?cs
			set:symbolFile = "dialog-error_tango.gif"
		?><?cs elif type == "environment_warning" ?><?cs
			set:symbolFile = "dialog-error_tango.gif"
		?><?cs elif type == "hint" ?><?cs
			set:symbolFile = "dialog-warning_tango.gif"
		?><?cs /if
	?><?cs # preparations are done - now start writing
	?><fieldset class="message"><table><tr><td class="message_symbol"><img src="<?cs
		call:link('cryptobox-misc/' + symbolFile,'','','','')
		?>" alt="icon: info" /></td><?cs
	# check if it is a 'normal' message ?><?cs
	if:subcount(Lang[category][mname]) > 0 ?><?cs
		call:show_messageNode(Lang[category][mname]) ?><?cs
	# check if the mname starts with "Plugins." ... ?><?cs
	elif:(string.slice(mname,0,8) == "Plugins.") && subcount(Lang[plugPrefix][category][plugSuffix]) > 0 ?><?cs
		call:show_messageNode(Lang[plugPrefix][category][plugSuffix]) ?><?cs
	# the message does not seem to exist ... ?><?cs
	else ?>
		<td><h1>unknown <?cs var:type ?> message</h1>
		could not find <?cs var:type ?> message: '<?cs var:mname ?>'</td><?cs
	/if ?></tr></table></fieldset><?cs
/def ?><?cs


def:environment_warning(mname)
	?><?cs call:message_dispatch(mname, "environment_warning", "EnvironmentWarning") ?><?cs
/def ?><?cs


def:hint(mname) ?><?cs
# show a warning hint
	?><?cs call:message_dispatch(mname, "hint", "AdviceMessage") ?><?cs
/def ?><?cs


def:warning(mname)
	?><?cs call:message_dispatch(mname, "warning", "WarningMessage") ?><?cs
/def ?><?cs


def:success(mname)
	?><?cs call:message_dispatch(mname, "success", "SuccessMessage") ?><?cs
/def ?><?cs


def:print_form_header(form_name, action) ?><?cs #
# the header of a form - including Setting.LinkAttrs
	?><form name="<?cs var:html_escape(form_name) ?>" action="<?cs call:link(action,"","","","") ?>" method="post" enctype="application/x-www-form-urlencoded" accept-charset="utf-8"><?cs
/def ?><?cs


def:show_volume_icon(volume) ?><?cs
# show the appropriate icon for the current state of the volume ?><?cs
	if:volume.active ?><?cs
		if:volume.encryption ?><?cs
			if:volume.busy ?><?cs
				set:filename='volume_active_crypto_busy.gif' ?><?cs
			else ?><?cs
				set:filename='volume_active_crypto.gif' ?><?cs
			/if ?><?cs
		else ?><?cs
			if:volume.busy ?><?cs
				set:filename='volume_active_plain_busy.gif' ?><?cs
			else ?><?cs
				set:filename='volume_active_plain.gif' ?><?cs
			/if ?><?cs
		/if ?><?cs
	else ?><?cs
		if:volume.encryption ?><?cs
			if:volume.busy ?><?cs
				set:filename='volume_passive_crypto_busy.gif' ?><?cs
			else ?><?cs
				set:filename='volume_passive_crypto.gif' ?><?cs
			/if ?><?cs
		else ?><?cs
			if:volume.busy ?><?cs
				set:filename='volume_passive_plain_busy.gif' ?><?cs
			else ?><?cs
				set:filename='volume_passive_plain.gif' ?><?cs
			/if ?><?cs
		/if ?><?cs
	/if ?><img src="<?cs call:link('cryptobox-misc/' + filename,'','','','') ?>" alt="icon: volume" /><?cs
/def ?><?cs


def:show_volume(volume) ?><?cs
# show the icon of the volume ?>
	<div class="volume">
		<a href="<?cs call:link('volume_mount','device',volume.device,'','') ?>" title="<?cs var:html_escape(volume.name) ?>">
			<?cs call:show_volume_icon(volume) ?><br/><?cs
				var:html_escape(volume.name) ?> (<?cs
				var:html_escape(volume.size) ?>)</a></div><?cs
/def ?><?cs


def:reload_link(attr, value) ?><?cs
# construct a link to reload the current page, but change/set one paramter
	?><?cs # first: override previous content of "Temp"
	?><?cs each:attrs = Temp
		?><?cs set:attrs = ""
	?><?cs /each
	?><?cs each:attrs = Data.ScriptParams
		?><?cs # do not keep _all_ params - just the necessary ones
				otherwise it could happen, that a previous action is repeated
				accidently by reloading - or given passwords can be exposed in the url
		?><?cs if:(name(attrs) != "action") && (name(attrs) != "store") ?><?cs
			set:Temp[name(attrs)] = attrs ?><?cs /if
		?><?cs /each
	?><?cs if:attr != "" ?><?cs set:Temp[attr] = value ?><?cs /if
	?><?cs set:first_attr = 1
	?><?cs each:attrs = Temp
		?><?cs if:(name(attrs) != "") && (attrs != "")
			?><?cs if:first_attr ?>?<?cs
					set:first_attr = 0 ?><?cs
				else
				?>&amp;<?cs /if
			?><?cs var:url_escape(name(attrs)) ?>=<?cs var:url_escape(attrs)
		?><?cs /if
	?><?cs /each
	?><?cs
 /def ?><?cs


def:help_link() ?><?cs
# show a link for enabling or disabling the help texts ?>
	<div class="help_link">
		<?cs if:Settings.Help ?>
			<a href="<?cs call:reload_link("help","0") ?>"
					title="<?cs var:html_escape(Lang.Button.DisableHelp) ?>">
				<?cs var:html_escape(Lang.Button.DisableHelp) ?><?cs
				set:icon_file = "icon_get_help_disable.png" ?><?cs
		else ?>
			<a href="<?cs call:reload_link("help","1") ?>"
					title="<?cs var:html_escape(Lang.Button.EnableHelp) ?>">
				<?cs var:html_escape(Lang.Button.EnableHelp) ?><?cs
				set:icon_file = "icon_get_help.png" ?><?cs
		/if ?>
			<img class="message_symbol" src="cryptobox-misc/<?cs var:icon_file ?>" alt="icon: help" />
			</a></div><?cs
 /def ?><?cs


def:show_help(text) ?><?cs
# display a help text if the help setting is turned on
	?><?cs if:Settings.Help ?><div class="help_text"><?cs var:html_escape(text)
	?></div><?cs /if ?><?cs
 /def ?><?cs


def:handle_messages() ?><?cs
# call this function once for every page - otherwise your risk to loose messages
# if it gets called twice somehow, then we just ignore it
	?><?cs if:!messages_are_handled
		?><?cs if:Data.Warning ?><?cs call:warning(Data.Warning) ?><?cs /if
		?><?cs if:Data.Success ?><?cs call:success(Data.Success) ?><?cs /if
		?><?cs set:messages_are_handled = 1
	?><?cs /if ?><?cs
 /def ?><?cs

def:show_plugin_title() ?>
	<div class="plugin_system_title">
		<img alt="icon: <?cs var:html_escape(Data.ActivePlugin) ?>" src="icons/<?cs
				var:html_escape(Data.ActivePlugin) ?>" />
		<h1><?cs var:Lang.Plugins[Data.ActivePlugin].Title ?></h1>
	</div><?cs 
/def ?><?cs

def:show_plugin_icon() ?>
		<img alt="icon: <?cs var:html_escape(Data.ActivePlugin) ?>" src="icons/<?cs
				var:html_escape(Data.ActivePlugin) ?>" /> <?cs
/def ?><?cs

# show the icons of all system plugins ?><?cs
def:show_system_plugin_overview() ?>
	<div class="plugin_system_overview">
	<?cs loop: order = #0, #100, #1
		?><?cs # plugins ?><?cs each:x = Settings.PluginList
			?><?cs if:x.Types.system && x.Visible.preferences && x.Rank == order ?>
				<a href="<?cs
					call:link(name(x),'','','','') ?>" title="<?cs
					var:html_escape(Lang.Plugins[name(x)].Link) ?>"><img src="<?cs
					call:link('icons/' + name(x), '','','','') ?>" alt="<?cs
					var:html_escape('icon: ' + x.Name) ?>" />
				<?cs
			/if ?><?cs
		/each ?><?cs
	/loop ?>
	</div>
<?cs /def ?>

