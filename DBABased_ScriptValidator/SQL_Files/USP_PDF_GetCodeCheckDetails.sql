
SET XACT_ABORT ON
SET NOCOUNT ON 
GO

CREATE OR ALTER PROCEDURE USP_PDF_GetValidatorExecutionLog
@arg_PackageID INT ,
@arg_ExecDate DATETIME,
@arg_proceeName VARCHAR(500),
@arg_Status INT,
@arg_Ismailsent INT

AS

DECLARE @vr_packageName VARCHAR(1000)

IF (@arg_PackageID IS NOT NULL AND @arg_ExecDate IS NOT NULL)

BEGIN
	SELECT @vr_packageName =Name FROM SVN_BranchOrPackages WITH(NOLOCK) WHERE package_id=@arg_PackageID

	IF EXISTS(SELECT TOP 1 1 FROM [DBO].SVNInvalidToolLog WITH(NOLOCK) WHERE PackageID=@arg_PackageID and DateOfExecution=@arg_ExecDate )
	BEGIN
		IF @arg_Status = 1
		BEGIN
		UPDATE [DBO].SVNInvalidToolLog SET STATUS =@arg_Status ,MailSENT =@arg_Ismailsent WHERE PackageID=@arg_PackageID and DateOfExecution=@arg_ExecDate
		SELECT 'UPDATED[Sucessfull]' 
		END
		ELSE IF @arg_Status = 3
		BEGIN
		UPDATE [DBO].SVNInvalidToolLog SET STATUS =@arg_Status,MailSENT =@arg_Ismailsent WHERE PackageID=@arg_PackageID and DateOfExecution=@arg_ExecDate
		SELECT 'UPDATED[Exception]' 
		END


	END
	ELSE
	BEGIN
		INSERT INTO [DBO].SVNInvalidToolLog(PackageID,ProcessName,DateOfExecution,PackageName,Status,MailSENT)
		SELECT @arg_PackageID,@arg_proceeName,@arg_ExecDate,@vr_packageName,0,@arg_Ismailsent
		SELECT 'STARTED'
	END
END

