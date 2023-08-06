adpasswd.py: Pure Python Command line interface to change Active Directory Passwords via LDAP.

SETUP:
	you need a config file.
	config files can either be in the Current Working Directory, or in ~/
	config files are always named .adpasswd.cfg and are INI style.
	
Example:
	
		[ad]
	host: ad.blah.com
	port: 636
	binddn: cn=Administrator,CN=Users,DC=ad,DC=blah,DC=com
	bindpw: changemequickly	
	searchdn: DC=ad,DC=blah,DC=com

All of the options above MUST exist, and be configured properly for this to work.

Once you have a config file setup, then it's EASY to use:
	adpasswd.py username [password]


you can call it with a password or not, if you don't you will be prompted for one.

you get NO OUTPUT (but successful return) if everything went well. (good for scripts!)
If things went wrong, you will be told about it.


Bug reports, etc please use launchpad: https://launchpad.net/adpasswd

CREDITS:
	ldaplib.py originally from scmgre@users.sourceforge.net
	URL: http://sourceforge.net/projects/ldaplibpy/
	Big thanks for doing all the hard work!