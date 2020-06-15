SELECT p.* FROM physician p LIMIT 3;
SELECT phy.name AS 'Physician', pat.name AS 'Patient' FROM physician phy, patient pat WHERE phy.employeeid = pat.pcp;
SELECT phy.name, pat.name FROM physician phy INNER JOIN patient pat ON phy.employeeid = pat.pcp;
SELECT * FROM block;
SELECT DISTINCT pcp FROM patient;
SELECT name, employeeid, ssn FROM nurse WHERE registered='t' or position = 'Nurse' ORDER BY name, employeeid;
INSERT INTO patient VALUES(10, 'AJ', 'Somewhere', '1234567890', 1, 2);