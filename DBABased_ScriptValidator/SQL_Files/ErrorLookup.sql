USE Ankit_ValidatorDB
GO

DROP TABLE IF EXISTS ValidatorErrorLookup
Go
CREATE TABLE ValidatorErrorLookup (
Eid VARCHAR(100) NOT NULL,
ErrorName  VARCHAR(200) ,
Plat INT ,
Credit INT 
PRIMARY KEY	(Eid)

)

INSERT INTO ValidatorErrorLookup
SELECT 'Err01','ALTERTableCheck',1,1 UNION ALL
SELECT 'Err02','TriggerCheck',1,1 UNION ALL
SELECT 'Err03','ViewCheck',1,1 UNION ALL
SELECT 'Err04','IndexCheck',1,1 UNION ALL
SELECT 'Err05','NoCountCheck',1,1 UNION ALL
SELECT 'Err06','QuotedIdentifierCheck',1,0 UNION ALL
SELECT 'Err07','SynonymLocalCheck',1,1 UNION ALL
SELECT 'Err08','AlterColumnCheck',1,1  UNION ALL
SELECT 'Err09','UID_check',1,1  UNION ALL
SELECT 'Err10','OrphanFileCheck',1,1 UNION ALL
SELECT 'Err11','AsteriskCheck',1,1	UNION ALL
SELECT 'Err12','ProcDBOCheck',1,1	UNION ALL
SELECT 'Err13','CheckDropProc',1,1	UNION ALL
SELECT 'Err14','DBBIndexCheck',1,1	UNION ALL
SELECT 'Err15','SynonymsDBOCheck',1,1 UNION ALL
SELECT 'Err16','ReportingIndexCheck',1,1 UNION ALL
SELECT 'Err17','IndexMaxDOPCheck',1,1 UNION ALL
SELECT 'Err18','IndexONLINECheck',1,1 UNION ALL

SELECT 'Err555','PerformanceCheck',1,1 