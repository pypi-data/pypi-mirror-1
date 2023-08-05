<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<?cs # $Id: header.cs 790 2007-02-08 02:16:41Z lars $ ?>

<head>
	<title>CryptoBox</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta http-equiv="pragma" content="no-cache" />
	<meta http-equiv="cache-control" content="no-cache" />
	<meta http-equiv="expires" content="0" />
	<link rel="shortcut icon" href="/favicon.ico" />
	<link rel="stylesheet" media="screen" href="<?cs var:Settings.Stylesheet ?>" type="text/css" />
	<?cs if:?Data.Redirect.URL ?><meta http-equiv="refresh" content="<?cs var:Data.Redirect.Delay ?>;url=<?cs var:Data.Redirect.URL ?>" /><?cs
	elif:Data.Redirect.Action ?><meta http-equiv="refresh" content="<?cs var:Data.Redirect.Delay ?>;url=<?cs call:link(Data.Redirect.Action,'','','','') ?>" /><?cs /if ?>

<?cs # any additional (plugin) stylesheets? ?><?cs
if:subcount(Data.StylesheetFiles) > 0
	?><style type="text/css"><?cs
	each:css_file = Data.StylesheetFiles ?><?cs
		linclude:css_file ?><?cs
	/each ?></style><?cs
/if ?>

</head>
<body>


<div id="main">

<div id="main_menu">
	<?cs # three possibilities to find the active ('to be marked') plugin:
			- the active plugin is a volume plugin -> mark 'disks'
			- the active plugin is part of the menu list -> mark it
			- the rest: mark 'preferences' ?><?cs
	if:Settings.PluginList[Data.ActivePlugin].Types.volume ?><?cs
		set:markPlugin = 'disks' ?><?cs
	else ?><?cs
		# first: set default value ?><?cs
		set:markPlugin = 'system_preferences' ?><?cs
		# check if the active plugin is visible in the menu ?><?cs
		each:plugin = Settings.PluginList ?><?cs
			if:plugin.Visible.menu && (name(plugin) == Data.ActivePlugin) ?><?cs
				set:markPlugin = name(plugin) ?><?cs
			/if ?><?cs
		/each ?><?cs
	/if ?><?cs
	# sort the Plugins - using the most stupid way :) ?><?cs
	loop: order = #0, #100, #1 ?><?cs
		# plugins ?><?cs each:x = Settings.PluginList ?><?cs
			if:x.Types.system && x.Visible.menu && x.Rank == order ?>
				<div class="plugin_menu plugin_menu_<?cs
					if:markPlugin == name(x) ?>active<?cs else ?>passive<?cs /if
					?>"><a href="<?cs call:link(name(x),'','','','') ?>" title="<?cs
						var:html_escape(Lang.Plugins[name(x)].Link) ?>"><img src="<?cs
						call:link('icons/' + name(x), '','','','') ?>" alt="<?cs
						var:html_escape('icon: ' + name(x)) ?>" /><br/><?cs
					var:html_escape(Lang.Plugins[name(x)].Link) ?></a></div><?cs
				/if ?><?cs
			/each ?><?cs
		/loop ?>
</div>



<?cs # we need this div to get 100% of screenwidth in mozilla and ie ?>
<div id="pane_div">
<table id="pane">

	<tr><td colspan="3"><div id="head">
		<table>
		<tr><td>
			<h1><?cs var:html_escape(Lang.Title.Top) ?></h1>
			<h2><?cs var:html_escape(Lang.Title.Slogan) ?></h2>
			</td>
		<td>
			<?cs if:Data.activeDisksCount > 0 ?><?cs
				set:logoFile = "cbx-text-logo2.png" ?><?cs
			  else ?><?cs
				set:logoFile = "cbx-text-logo1.png" ?><?cs
			/if ?>
			<div class="logo"><a href="<?cs call:link("", "", "", "", "")
					?>" title="CryptoBox"><img src="cryptobox-misc/<?cs var:logoFile
					?>" alt="icon: logo" />
			</a></div>
			<?cs call:help_link() ?>
		</td></tr></table>
	</div></td></tr>

	<?cs if:subcount(Data.EnvironmentWarning) > 0
		?><?cs # display up to 3 warnings (sorted by priority)
		?><?cs set:warn_count = min(#3, subcount(Data.EnvironmentWarning))
		?><?cs loop: x = #0, warn_count-#1, #1 ?>
			<tr><td colspan="3"><div class="EnvironmentWarning">
				<?cs call:environment_warning(Data.EnvironmentWarning[x]) ?>
				</div></td></tr>
		<?cs /loop ?><?cs
	/if ?>

<!--
		<tr><td id="pane_left_top" /><td id="pane_top" /><td id="pane_right_top" /></tr>
		<tr><td id="pane_left" />
			<td id="pane_content">
-->
		<tr><td><td id="pane_content">
    <div id="words">
	
