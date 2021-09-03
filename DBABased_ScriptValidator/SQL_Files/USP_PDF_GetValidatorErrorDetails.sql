USE Ankit_ValidatorDB
GO

--============

CREATE OR ALTER PROCEDURE USP_PDF_GetValidatorErrorDetails 

@arg_PackgeID VARCHAR(max) ,
@arg_FileLoc VARCHAR(max) ,
@arg_ErrorCode VARCHAR(201), 
@arg_ErrorMsg VARCHAR(max)
As

Drop Table if EXISTS #Temp_AuthorData
CREATE TABLE #Temp_AuthorData (
ID INT IDENTITY(1,1) ,
PACKAGEID INT  ,
FILEID INT ,
AUTHORNAME VARCHAR(500) ,
Processed INT Default 0
)

Declare @vr_FID VARCHAR(50)
Declare @vr_AuthorName VARCHAR(200)
Declare @vr_ID INT
Declare @vr_ErrCount iNT
Declare @vr_IstoCheck iNT

SET @vr_ErrCount =NULL
SET @vr_IstoCheck = 1

SELECT @vr_FID = ltrim(Rtrim(File_Id)) FROM [dbo].[SVN_Files] With(NOLOCk) WHERE Shared_Path =Ltrim(Rtrim(@arg_FileLoc)) 
and Package_ID = @arg_PackgeID

IF EXISTS (SELECT TOP 1 1 FROM DBO.CodeValidation_Exception WITH(NOLOCK) WHERE FILE_ID =@vr_FID AND Error =@arg_ErrorCode)
BEGIN
	SET @vr_IstoCheck = 0
END

-- @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

IF @vr_FID IS NOT NULL and @vr_FID <> 0 and @vr_IstoCheck =1
BEGIN
    -- #################################################
	Select Last_Author_Name , SVN_Location ,File_Name   FROM SVN_Files  With(NOLOCk) WHERE File_Id = @vr_FID
	-- #################################################

	IF NOT EXISTS (SELECT TOP 1 1 FROM ValidationErrorFilesSummary WITH(NOLOCK) WHERE FileID = @vr_FID AND  ErrorCode = @arg_ErrorCode)
	BEGIN

		INSERT INTO ValidationErrorFilesSummary (PackageID,FileID	,ErrorCode	,ErrorMessage ,ErrCount,MarkDeleted)
		SELECT @arg_PackgeID,@vr_FID ,@arg_ErrorCode ,@arg_ErrorMsg ,1,0

	END
	ELSE
	BEGIN
		SELECT @vr_ErrCount = ErrCount FROM  ValidationErrorFilesSummary WITH(NOLOCK) WHERE FileID =@vr_FID AND  ErrorCode = @arg_ErrorCode
		UPDATE ValidationErrorFilesSummary SET ErrCount = (@vr_ErrCount + 1 ),MarkDeleted =0 WHERE FileID =@vr_FID AND  ErrorCode = @arg_ErrorCode

	END

	-- ======================================================Inserting Author Details ===========================================================================
	INSERT INTO #Temp_AuthorData (PACKAGEID ,FILEID ,AUTHORNAME)
	SELECT  DISTINCT SA.File_Id,SA.Package_ID,SA.Author_Name FROM SVN_FileAuthorDetails SA WITH(NOLOCK) JOIN
	ValidationErrorFilesSummary VF WITH(NOLOCK) on (SA.File_Id =VF.FileID) and (SA.Package_ID = VF.PackageID)
	WHERE SA.File_Id =@vr_FID and VF.PackageID = @arg_PackgeID and VF.MarkDeleted = 0

	WHILE EXISTS (SELECT TOP 1 1 FROM #Temp_AuthorData WHERE Processed =0)
		BEGIN
			SET @vr_AuthorName = NULL
			SET @vr_ID =NULL
		

			SELECT TOP 1 @vr_AuthorName = Ltrim(Rtrim(AUTHORNAME)) ,@vr_ID =ID FROM #Temp_AuthorData WHERE Processed = 0

			IF EXISTS (SELECT TOP 1 1 FROM [DBO].SVNAuthor_EmailLookup WITH(NOLOCK) WHERE SVNAuthorName =Ltrim(RTRIM(@vr_AuthorName)) and IsConfig = 0)
			BEGIN
				SELECT @vr_AuthorName = Ltrim(RTRIM(EmailUserName)) FROM [DBO].SVNAuthor_EmailLookup WITH(NOLOCK)  WHERE SVNAuthorName =Ltrim(RTRIM(@vr_AuthorName))
			END

			IF NOT EXISTS (SELECT TOP 1 1 FROM DBO.ValidatorMailDetail WITH(NOLOCK) WHERE FileID = @vr_FID and PackageID = @arg_PackgeID and AuthorsName =@vr_AuthorName )
			BEGIN
				INSERT INTO DBO.ValidatorMailDetail (PackageID ,FileID ,AuthorsName ,MailID)
				SELECT @arg_PackgeID ,@vr_FID ,@vr_AuthorName ,@vr_AuthorName+'@corecard.com'
			END

			UPDATE #Temp_AuthorData SET Processed = 2 WHERE Processed = 0 and ID = @vr_ID
		END
END
ELSE
BEGIN
	SELECT 0
END