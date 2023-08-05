#
# Copyright 2007 sense.lab e.V.
# 
# This file is part of the CryptoBox.
#
# The CryptoBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# The CryptoBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the CryptoBox; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""Create an SSL certificate to encrypt the webinterface connection via stunnel

requires:
 - stunnel (>= 4.0)
 - "M2Crypto" python module
"""

__revision__ = "$Id"

import cryptobox.plugins.base
import subprocess
import os
import cherrypy

CERT_FILENAME = 'cryptobox-ssl-certificate.pem'
KEY_BITS = 1024
ISSUER_INFOS = {
		"ST": "SomeIssuerState",
		"L": "SomeIssuerLocality",
		"O": "SomeIssuerOrganization",
		"OU": "CryptoBox-ServerIssuer",
		"CN": "cryptoboxIssuer",
		"emailAddress": "infoIssuer@cryptobox.org"}
CERT_INFOS = {
		"ST": "SomeState",
		"L": "SomeLocality",
		"O": "SomeOrganization",
		"OU": "CryptoBox-Server",
		"CN": "*",
		"emailAddress": "info@cryptobox.org"}
EXPIRE_TIME = 60*60*24*365*20	# 20 years forward and backward
SIGN_DIGEST = "md5"
PID_FILE = os.path.join("/tmp/cryptobox-stunnel.pid")


class encrypted_webinterface(cryptobox.plugins.base.CryptoBoxPlugin):
	"""Provide an encrypted webinterface connection via stunnel
	"""

	plugin_capabilities = [ "system" ]
	plugin_visibility = []
	request_auth = True
	rank = 80

	def do_action(self):
		"""The action handler.
		"""
		return None


	def get_status(self):
		"""Retrieve the current state of the webinterface connection
		"""
		if self.__is_encrypted():
			return "1"
		else:
			return "0"


	def get_warnings(self):
		"""check if the connection is encrypted
		"""
		warnings = []
		## check if m2crypto is available
		try:
			import M2Crypto
		except ImportError:
			warnings.append((45, "Plugins.%s.MissingModuleM2Crypto" % self.get_name()))
		if not os.path.isfile(self.root_action.STUNNEL_BIN):
			warnings.append((44, "Plugins.%s.MissingProgramStunnel" % self.get_name()))
		if not self.__is_encrypted():
			## plaintext connection -> "heavy security risk" (priority=20..39)
			warnings.append((25, "Plugins.%s.NoSSL" % self.get_name()))
		return warnings
	

	def __is_encrypted(self):
		"""perform some checks for encrypted connections
		"""
		if cherrypy.request.scheme == "https":
			return True
		## check an environment setting - this is quite common behind proxies
		if os.environ.has_key("HTTPS"):
			return True
		## check if it is a local connection (or via stunnel)
		if cherrypy.request.headers.has_key("Remote-Host") \
				and (cherrypy.request.headers["Remote-Host"] == "127.0.0.1"):
			return True
		## the arbitrarily chosen header is documented in README.proxy
		if cherrypy.request.headers.has_key("X-SSL-Request") \
				and (cherrypy.request.headers["X-SSL-Request"] == "1"):
			return True
		## it looks like a plain connection
		return False
	

	def handle_event(self, event, event_info=None):
		"""Create a certificate during startup (if it does not exist) and run stunnel
		"""
		if event == "bootup":
			cert_abs_name = self.cbox.prefs.get_misc_config_filename(CERT_FILENAME)
			if not os.path.isfile(cert_abs_name):
				try:
					cert = self.__get_certificate()
					self.cbox.prefs.create_misc_config_file(CERT_FILENAME, cert)
					self.cbox.log.info("Created new SSL certificate: %s" % \
							cert_abs_name)
					## make it non-readable for other users
					try:
						os.chmod(cert_abs_name, 0600)
					except OSError, err_msg:
						self.cbox.log.warn("Failed to change permissions of secret " \
								+ "certificate file (%s): %s" % \
								(cert_abs_name, err_msg))
				except IOError, err_msg:
					## do not run stunnel without a certificate
					self.cbox.log.warn("Failed to create new SSL certificate (%s): %s" \
							% (cert_abs_name, err_msg))
					return
			self.__run_stunnel(cert_abs_name)
		elif event == "shutdown":
			self.__kill_stunnel()
	

	def __kill_stunnel(self):
		"""try to kill a running stunnel daemon
		"""
		if not os.path.isfile(PID_FILE):
			self.cbox.log.warn("Could not find the pid file of a running stunnel " \
					+ "daemon: %s" % PID_FILE)
			return
		try:
			pfile = open(PID_FILE, "r")
			try:
				pid = pfile.read().strip()
			except IOError, err_msg:
				self.cbox.log.warn("Failed to read the pid file (%s): %s" % (PID_FILE, err_msg))
				pfile.close()
				return
			pfile.close()
		except IOError, err_msg:
			self.cbox.log.warn("Failed to open the pid file (%s): %s" % (PID_FILE, err_msg))
			return
		if pid.isdigit():
			pid = int(pid)
		else:
			return
		try:
			## SIGTERM = 15
			os.kill(pid, 15)
			self.cbox.log.info("Successfully stopped stunnel")
			try:
				os.remove(PID_FILE)
			except OSError, err_msg:
				self.cbox.log.warn("Failed to remove the pid file (%s) of stunnel: %s" \
						% (PID_FILE, err_msg))
		except OSError, err_msg:
			self.cbox.log.warn("Failed to kill stunnel process (PID: %d): %s" % \
					(pid, err_msg))


	def __run_stunnel(self, cert_name, dest_port=443):
		## retrieve currently requested port (not necessarily the port served
		## by cherrypy - e.g. in a proxy setup)
		request_port = cherrypy.config.get("server.socket_port", 80)
		self.cbox.log.debug("[encrypted_webinterface] starting " \
				+ "%s on port %s for %s" % \
				(self.root_action.STUNNEL_BIN, dest_port, request_port))
		proc = subprocess.Popen(
			shell = False,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			args = [
				self.cbox.prefs["Programs"]["super"],
				self.cbox.prefs["Programs"]["CryptoBoxRootActions"],
				"plugin", os.path.join(self.plugin_dir, "root_action.py"),
				cert_name,
				str(request_port),
				str(dest_port),
				PID_FILE ])
		(output, error) = proc.communicate()
		if proc.returncode == 0:
			self.cbox.log.info("Successfully started 'stunnel'")
			return True
		else:
			self.cbox.log.warn("Failed to run 'stunnel': %s" % error)
			return False


	def __get_certificate(self):
		"""Create a self-signed certificate and return its pem content
		
		The code is mainly inspired by:
		https://dev.tribler.org/browser/m2crypto/trunk/contrib/SimpleX509create.py
		"""
		import M2Crypto
		import time
		string_type = 0x1000 | 1	# see http://www.koders.com/python/..
				# ../fid07A99E089F55187896A06CD4E0B6F21B9B8F5B0B.aspx?s=bavaria
		key_gen_number = 0x10001	# commonly used for key generation: 65537
		rsa_key = M2Crypto.RSA.gen_key(KEY_BITS, key_gen_number, callback=lambda: None)
		rsa_key2 = M2Crypto.RSA.gen_key(KEY_BITS, key_gen_number, callback=lambda: None)
		pkey = M2Crypto.EVP.PKey(md=SIGN_DIGEST)
		pkey.assign_rsa(rsa_key)
		sign_key = M2Crypto.EVP.PKey(md=SIGN_DIGEST)
		sign_key.assign_rsa(rsa_key2)
		subject = M2Crypto.X509.X509_Name()
		for (key, value) in CERT_INFOS.items():
			subject.add_entry_by_txt(key, string_type, value, -1, -1, 0)
		issuer = M2Crypto.X509.X509_Name(M2Crypto.m2.x509_name_new())
		for (key, value) in ISSUER_INFOS.items():
			issuer.add_entry_by_txt(key, string_type, value, -1, -1, 0)
		## time object
		asn_time1 = M2Crypto.ASN1.ASN1_UTCTIME()
		asn_time1.set_time(long(time.time()) - EXPIRE_TIME)
		asn_time2 = M2Crypto.ASN1.ASN1_UTCTIME()
		asn_time2.set_time(long(time.time()) + EXPIRE_TIME)
		request = M2Crypto.X509.Request()
		request.set_subject_name(subject)
		request.set_pubkey(pkey)
		request.sign(pkey=pkey, md=SIGN_DIGEST)
		cert = M2Crypto.X509.X509()
		## always create a unique version number
		cert.set_version(0)
		cert.set_serial_number(long(time.time()))
		cert.set_pubkey(pkey)
		cert.set_not_before(asn_time1)
		cert.set_not_after(asn_time2)
		cert.set_subject_name(request.get_subject())
		cert.set_issuer_name(issuer)
		cert.sign(pkey, SIGN_DIGEST)
		result = ""
		result += cert.as_pem()
		result += pkey.as_pem(cipher=None)
		return result

