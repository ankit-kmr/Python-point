			===================================================================
				WinRM Plugins for Remote Connections and Managements
			===================================================================
Component of the Windows Hardware Management features that manage server hardware locally and remotely.
Allows to write applications that communicate remotely through the WS-Management protocol.


Configuration requirements
-----------------------------
WinRM is automatically installed with all currently-supported versions of the Windows operating system.
The WinRM service starts automatically on Windows Server 2008 and on wards.

On "Client remote server" need to look into below mentioned configuration parts for 
Winrm command-line tool to perform data operations :

    * POWERSHELL version should be > 3.0
    >> Get-Host | Select-Object Version .


    * To veiw current winRM Listener (WinRM services listens for requests on one or more ports. 
    Each of these ports must have a listener created and configured.)
    command to locate listeners and the addresses:
    >> winrm enumerate winrm/config/Listener

    * Listeners are defined by a transport (HTTP or HTTPS) and an IPv4 or IPv6 address.
    The default HTTP port is 5985 and HTTPs is 5986.
    Command to create default settings for a listener :
    >> winrm quickconfig
    
    
    * On private networks, the default Windows Firewall rule for PowerShell Remoting accepts all 
    connections. On public networks, the default Windows Firewall rule allows PowerShell Remoting 
    connections only from within the same subnet.)
    Command to get network profile :
    >> Get-NetConnectionProfile
    Command to change network type :
    >> Set-NetConnectionProfile -NetworkCategory Private


    * For winRM inbond requests at server endpoint need to add firewall exception (inbound rule) 
    for port 5986(https)
    Command to do so :
    >> netsh advfirewall firewall add rule name="Windows Remote Management (HTTPS-In)" dir=in action=allow protocol=TCP localport=5986

    NOTE : intital authnticatio (Kerberos and NTLM) -- When a client connects to a domain server using its computer name, the default authentication protocol is Kerberos. 
    When a client connects to a domain server using its IP address, or connects to a workgroup server, 
    Kerberos authentication is not possible. In that case, PowerShell Remoting relies on the NTLM authentication protocol. 

  
