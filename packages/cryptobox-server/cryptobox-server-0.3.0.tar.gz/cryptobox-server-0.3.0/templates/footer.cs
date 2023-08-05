<?cs # $Id: footer.cs 747 2007-02-03 18:24:07Z age $ ?>

	<?cs if:Data.Redirect ?>
		<p class="warning"><a href="<?cs if:Data.Redirect.URL ?><?cs var:Data.Redirect.URL ?><?cs else ?><?cs call:link(Data.Redirect.Action,'','','','') ?><?cs /if ?>"><?cs var:html_escape(Lang.Text.RedirectNote) ?></a></p>
	<?cs /if ?>

    </div><!-- end of 'words' -->

	<?cs # ugly way of getting a 'min-height' for IE6 ?>

	<!-- </td><td id="pane_right"><p style="height:260px;" /></tr> -->
	</td><td><p style="height:260px;" /></tr>


	<tr><td/><td><div id="footer">
		<?cs var:Data.Version ?>&nbsp;&nbsp;
		<a href="http://cryptobox.org" title="<?cs var:html_escape(Lang.Text.ProjectHomePage) ?>">CryptoBox-Home</a>&nbsp;&nbsp;&nbsp;<?cs var:html_escape(Lang.Text.ProjectNote) ?>&nbsp;<a href="http://senselab.org/" title="systemausfall.org">sense.lab</a>
	</div></td><td/></tr>
	<?cs # ugly way of getting a 'min-width' for IE6 ?>
	<tr><td/><td><p style="width:600px;" /><td/></tr>

</table></div>


</div><!-- end of 'main' -->

<!-- CBOX-STATUS-begin - used for validation - do not touch!
Settings.Language=<?cs var:html_escape(Settings.Language) ?>
Data.Version=<?cs var:html_escape(Data.Version) ?>
Data.ScriptURL=<?cs var:html_escape(Data.ScriptURL) ?>
<?cs each:x = Data.Status.Plugins ?>Data.Status.Plugins.<?cs
	var:name(x) ?>=<?cs var: html_escape(x) ?>
<?cs /each
?>CBOX-STATUS-end -->

<!-- $Revision: 747 $ -->

<?cs # check, if the macro 'handle_messages' was called before - otherwise place a warning ?>
<?cs if:!messages_are_handled ?>MESSAGES WERE NOT HANDLED PROPERLY - PLEASE FIX THIS!<?cs /if ?>

</body>
</html>

