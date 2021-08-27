192.168.29.35 -- win VM  3389
==============================================================================================
OpenSSH
========================
* installing openssh server on window server to connect
 -->  Open a PowerShell window as an administrator
	--> Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'   {checking ssh status}
	--> Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

* Configure SSH service to run automatically.
* Add\Enable inbound firewall rule with local port 22  for all domains. 


WinRM Plugins for remote connect
===========================

POWERSHELL version should be > 3.0
Get-Host | Select-Object Version .