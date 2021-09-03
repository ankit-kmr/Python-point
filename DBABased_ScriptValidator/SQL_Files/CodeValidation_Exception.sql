
--Pacakge_id
--File_ID
--Error -

--Package_id , --For package it executed
--DateOfExecution--Date when executed
--Status --What was the status ,0 Started,1 Successful,3 There was error or exception whil execution


DROP TABLE IF EXISTS DBO.CodeValidation_Exception
GO
CREATE TABLE DBO.CodeValidation_Exception (
ID INT IDENTITY(1,1),
Pacakge_id INT ,
File_ID INT ,
Error VARCHAR(50)
)


INSERT INTO DBO.CodeValidation_Exception(Pacakge_id,File_ID,Error)
SELECT 2374 ,52828,'Err08'

-- SELECT * FROM DBO.CodeValidation_Exception

--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--


DROP TABLE IF EXISTS [DBO].SVNInvalidToolLog
GO
CREATE TABLE [DBO].SVNInvalidToolLog (
Skey INT IDENTITY(1,1),
PackageID INT ,
ProcessName VARCHAR(200),
DateOfExecution DATETIME ,
PackageName VARCHAR(500),
Status INT ,
MailSENT INT 
)

