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

* POWERSHELL version should be > 3.0
>> Get-Host | Select-Object Version .


* To veiw current winRM Listener (WinRM services listens for requests on one or more ports. Each of these ports must have a listener created and configured.)
>> winrm enumerate winrm/config/Listener


{ On client server }

>> Get-NetConnectionProfile

Network should be private for WinRM to work

>> Set-NetConnectionProfile -NetworkCategory Private


>> winrm quickconfig
Enable the WinRM firewall exception.
Configure LocalAccountTokenFilterPolicy to grant administrative rights remotely to local users.

press y/n.


>> New-SelfSignedCertificate -DnsName "DESKTOP-CEPCEIS" -CertStoreLocation Cert:\LocalMachine\My
Thumbprint                                Subject
----------                                -------
E1E4314D304C5A445CA949410497023A6857DB2D  CN=DESKTOP-CEPCEIS

>> winrm create winrm/config/Listener?Address=*+Transport=HTTPS '@{Hostname="DESKTOP-CEPCEIS"; CertificateThumbprint="E1E4314D304C5A445CA949410497023A6857DB2D"}'

Adding firewall exception (inbound rule) port 5986 for https
netsh advfirewall firewall add rule name="Windows Remote Management (HTTPS-In)" dir=in action=allow protocol=TCP localport=5986

To allow unencrypted communication
>> Set-Item -Path "WSMan:\localhost\Service\AllowUnencrypted" -Value $true

NOTE : once winRM is configured can change back the Network to Public as before

{ On the Host server }

Network should be private to configure winRm services
>> Set-NetConnectionProfile -NetworkCategory Private
>> winrm set winrm/config/service @{AllowUnencrypted="true"}

NOTE : once winRM is configured can change back the Network to Public as before