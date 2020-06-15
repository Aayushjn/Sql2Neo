CREATE DATABASE IF NOT EXISTS hosp;
USE hosp;


CREATE TABLE IF NOT EXISTS physician(employee_id INT PRIMARY KEY, name VARCHAR(70), position VARCHAR(100), ssn INT);

CREATE TABLE IF NOT EXISTS department(department_id INT PRIMARY KEY, name VARCHAR(70), head INT, FOREIGN KEY(head) REFERENCES physician(employee_id));

CREATE TABLE IF NOT EXISTS patient(ssn INT PRIMARY KEY, name VARCHAR(70), address VARCHAR(255), phone VARCHAR(12), insurance_id INT, pcp INT, FOREIGN KEY(pcp) REFERENCES physician(employee_id));

CREATE TABLE IF NOT EXISTS nurse(employee_id INT PRIMARY KEY, name VARCHAR(70), position VARCHAR(100), registered TINYINT(1), ssn INT);

CREATE TABLE IF NOT EXISTS appointment(appointment_id INT PRIMARY KEY, patient INT, prep_nurse INT DEFAULT NULL, physician INT, start_dt_time DATETIME, end_dt_time DATETIME, examination_room CHAR(1), FOREIGN KEY(prep_nurse) REFERENCES nurse(employee_id), FOREIGN KEY(physician) REFERENCES physician(employee_id), FOREIGN KEY(patient) REFERENCES patient(ssn));

CREATE TABLE IF NOT EXISTS block(block_floor INT, block_code INT, CONSTRAINT pk_block PRIMARY KEY(block_floor, block_code));

CREATE TABLE IF NOT EXISTS room(room_number INT PRIMARY KEY, room_type VARCHAR(100), block_floor INT, block_code INT, unavailable TINYINT(1), FOREIGN KEY(block_floor, block_code) REFERENCES block(block_floor, block_code));

CREATE TABLE IF NOT EXISTS procedure_record(code INT PRIMARY KEY, name VARCHAR(70), cost INT);

CREATE TABLE IF NOT EXISTS undergoes(patient INT, procedure_id INT, date DATETIME, physician INT, assisting_nurse INT, FOREIGN KEY(patient) REFERENCES patient(ssn),FOREIGN KEY(procedure_id) REFERENCES procedure_record(code), FOREIGN KEY(physician) REFERENCES physician(employee_id), FOREIGN KEY(assisting_nurse) REFERENCES nurse(employee_id));

CREATE TABLE IF NOT EXISTS trained(physician INT, treatment INT, certification_date DATE, certification_expires DATE, FOREIGN KEY(physician) REFERENCES physician(employee_id), FOREIGN KEY(treatment) REFERENCES procedure_record(code));


INSERT INTO physician VALUES
(1, 'John Dorian'      , 'Staff Internist'             , 111111111),
(2, 'Elliot Reid'      , 'Attending Physician'         , 222222222),
(3, 'Christopher Turk' , 'Surgical Attending Physician', 333333333),
(4, 'Percival Cox'     , 'Senior Attending Physician'  , 444444444),
(5, 'Bob Kelso'        , 'Head Chief of Medicine'      , 555555555),
(6, 'Todd Quinlan'     , 'Surgical Attending Physician', 666666666),
(7, 'John Wen'         , 'Surgical Attending Physician', 777777777),
(8, 'Keith Dudemeister', 'MD Resident'                 , 888888888),
(9, 'Molly Clock'      , 'Attending Psychiatrist'      , 999999999);

INSERT INTO department VALUES
(1, 'General Medicine', 4),
(2, 'Surgery'         , 7),
(3, 'Psychiatry'      , 9);

INSERT INTO patient VALUES
(100000001, 'John Smith'       , '42 Foobar Lane'    , '555-0256', 68476213, 1),
(100000002, 'Grace Ritchie'    , '37 Snafu Drive'    , '555-0512', 36546321, 2),
(100000003, 'Random J. Patient', '101 Omgbbq Street' , '555-1204', 65465421, 2),
(100000004, 'Dennis Doe'       , '1100 Foobaz Avenue', '555-2048', 68421879, 3);

INSERT INTO nurse VALUES
(101, 'Carla Espinosa' , 'Head Nurse', 1, 111111110),
(102, 'Laverne Roberts', 'Nurse'     , 1, 222222220),
(103, 'Paul Flowers'   , 'Nurse'     , 0, 333333330);

INSERT INTO appointment VALUES
(13216584, 100000001, 101 , 1, '2008-04-24 10:00:00', '2008-04-24 11:00:00', 'A'),
(59871321, 100000004, NULL, 4, '2008-04-26 10:00:00', '2008-04-26 11:00:00', 'C'),
(69879231, 100000003, 103 , 2, '2008-04-26 11:00:00', '2008-04-26 12:00:00', 'C'),
(76983231, 100000001, NULL, 3, '2008-04-26 12:00:00', '2008-04-26 13:00:00', 'C');

INSERT INTO block VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(3, 1),
(3, 2);

INSERT INTO room VALUES
(101, 'Single', 1, 1, 0),
(102, 'Single', 2, 1, 0),
(212, 'Single', 3, 2, 0);

INSERT INTO procedure_record VALUES
(1, 'Reverse Rhinopodoplasty'       , 1500),
(2, 'Obtuse Pyloric Recombobulation', 3750),
(3, 'Folded Demiophtalmectomy'      , 4500),
(4, 'Complete Walletectomy'         , 10000),
(5, 'Obfuscated Dermogastrotomy'    , 4899);

INSERT INTO undergoes VALUES
(100000001, 2, '2008-05-02 00:00:00', 3, 101),
(100000001, 3, '2008-05-10 00:00:00', 7, 101),
(100000004, 4, '2008-05-13 00:00:00', 3, 103);

INSERT INTO trained VALUES
(3, 1, '2008-01-01', '2008-12-31'),
(3, 2, '2008-01-01', '2008-12-31'),
(6, 2, '2008-01-01', '2008-12-31'),
(6, 5, '2007-01-01', '2007-12-31'),
(7, 1, '2008-01-01', '2008-12-31');
