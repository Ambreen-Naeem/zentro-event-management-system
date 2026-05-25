USE master;
GO

IF EXISTS (SELECT * FROM sys.server_principals WHERE name = 'ems_user')
    DROP LOGIN ems_user;
GO

CREATE LOGIN ems_user
WITH PASSWORD = 'Password123',
CHECK_POLICY = OFF;
GO

IF DB_ID('EventManagementSys') IS NOT NULL
    DROP DATABASE EventManagementSys;
GO

CREATE DATABASE EventManagementSys;
GO

USE EventManagementSys;
GO

IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'ems_user')
    DROP USER ems_user;
GO

CREATE USER ems_user FOR LOGIN ems_user;
GO

ALTER ROLE db_owner ADD MEMBER ems_user;
GO

ALTER LOGIN ems_user ENABLE;
GO
USE EventManagementSys;
Go
ALTER ROLE db_owner ADD MEMBER ems_user;
SELECT name, is_disabled
FROM sys.server_principals
WHERE name = 'ems_user';

IF OBJECT_ID('Payments') IS NOT NULL DROP TABLE Payments;
IF OBJECT_ID('Tickets') IS NOT NULL DROP TABLE Tickets;
IF OBJECT_ID('Event_Registration') IS NOT NULL DROP TABLE Event_Registration;
IF OBJECT_ID('Events') IS NOT NULL DROP TABLE Events;
IF OBJECT_ID('Venues') IS NOT NULL DROP TABLE Venues;
IF OBJECT_ID('Organizers') IS NOT NULL DROP TABLE Organizers;
IF OBJECT_ID('Attendee') IS NOT NULL DROP TABLE Attendee;

------------------------------------------------------------
-- 1. ATTENDEE TABLE
------------------------------------------------------------
CREATE TABLE Attendee (
    attendee_id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20)
);

------------------------------------------------------------
-- 2. ORGANIZERS TABLE
------------------------------------------------------------
CREATE TABLE Organizers (
    organizer_id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    organization_name VARCHAR(100)
);

------------------------------------------------------------
-- 3. VENUES TABLE
------------------------------------------------------------
CREATE TABLE Venues (
    venue_id INT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(200),
    capacity INT CHECK (capacity >= 0)
);

------------------------------------------------------------
-- 4. EVENTS TABLE
------------------------------------------------------------
CREATE TABLE Events (
    event_id INT PRIMARY KEY,
    organizer_id INT,
    venue_id INT,
    title VARCHAR(100),
    description VARCHAR(300),
    start_datetime DATETIME,
    end_datetime DATETIME,
    capacity INT,
    status VARCHAR(20) DEFAULT 'scheduled',

    CONSTRAINT FK_Events_Organizers FOREIGN KEY (organizer_id)
        REFERENCES Organizers(organizer_id),

    CONSTRAINT FK_Events_Venues FOREIGN KEY (venue_id)
        REFERENCES Venues(venue_id)
);

------------------------------------------------------------
-- 5. EVENT REGISTRATION TABLE
------------------------------------------------------------
CREATE TABLE Event_Registration (
    registration_id INT PRIMARY KEY,
    attendee_id INT,
    event_id INT,
    registration_datetime DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_Reg_Attendee FOREIGN KEY (attendee_id)
        REFERENCES Attendee(attendee_id),

    CONSTRAINT FK_Reg_Event FOREIGN KEY (event_id)
        REFERENCES Events(event_id)
);

------------------------------------------------------------
-- 6. TICKETS TABLE
------------------------------------------------------------
CREATE TABLE Tickets (
    ticket_id INT PRIMARY KEY,
    registration_id INT,
    ticket_type VARCHAR(20),
    price DECIMAL(10,2),

    CONSTRAINT FK_Tickets_Registration FOREIGN KEY (registration_id)
        REFERENCES Event_Registration(registration_id)
);

------------------------------------------------------------
-- 7. PAYMENTS TABLE
------------------------------------------------------------
CREATE TABLE Payments (
    payment_id INT PRIMARY KEY,
    ticket_id INT,
    amount DECIMAL(10,2),
    payment_method VARCHAR(20),
    payment_datetime DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_Payments_Ticket FOREIGN KEY (ticket_id)
        REFERENCES Tickets(ticket_id)
);

------------------------------------------------------------
-- INSERT DATA
------------------------------------------------------------

-- ATTENDEES
INSERT INTO Attendee VALUES
(1, 'Sameea Amjad', 'sam@uni.com', '03001234567'),
(2, 'Ambreen Naeem', 'ambreen@uni.com', '03004567891'),
(3, 'Sadaf Iqbal', 'sadaf@uni.com', '03001112223'),
(4, 'Sara Ahmed', 'sara@uni.com', '03007654321'),
(5, 'Usman Iqbal', 'usman@uni.com', '03003455678');

-- ORGANIZERS
INSERT INTO Organizers VALUES
(1, 'Evently Pvt Ltd', 'contact@evently.com', 'Evently Pvt Ltd'),
(2, 'Techo', 'info@techo.com', 'Techo'),
(3, 'Creative Minds', 'hello@creativeminds.com', 'Creative Minds'),
(4, 'Global Expo', 'support@globalexpo.com', 'Global Expo'),
(5, 'Future Events', 'team@futureevents.com', 'Future Events');

-- VENUES
INSERT INTO Venues VALUES
(1, 'Expo Center Hall A', 'Main Boulevard, Lahore', 500),
(2, 'Tech Hub Auditorium', 'Gulshan-e-Iqbal, Karachi', 300),
(3, 'Royal Banquet Hall', 'F-7 Islamabad', 200),
(4, 'City Conference Center', 'Cantt, Rawalpindi', 400),
(5, 'Skyline Convention Hall', 'Bahria Town, Lahore', 600);

-- EVENTS
INSERT INTO Events VALUES
(1, 1, 1, 'Tech Expo 2025', 'Annual technology exhibition',
 '2025-02-10 10:00:00', '2025-02-10 18:00:00', 450, 'scheduled'),

(2, 2, 2, 'AI Workshop', 'Hands-on session on AI and ML',
 '2025-03-05 09:00:00', '2025-03-05 16:00:00', 250, 'scheduled'),

(3, 3, 3, 'Startup Meetup', 'Networking event for startups',
 '2025-04-12 14:00:00', '2025-04-12 18:00:00', 180, 'scheduled'),

(4, 4, 4, 'Business Summit', 'International business forum',
 '2025-05-20 10:00:00', '2025-05-20 17:00:00', 350, 'scheduled'),

(5, 5, 5, 'Developers Conference', 'Software developers event',
 '2025-06-15 09:00:00', '2025-06-15 19:00:00', 550, 'scheduled');

-- REGISTRATIONS
INSERT INTO Event_Registration VALUES
(1, 1, 1, GETDATE()),
(2, 2, 1, GETDATE()),
(3, 3, 2, GETDATE()),
(4, 4, 3, GETDATE()),
(5, 5, 4, GETDATE());

-- TICKETS
INSERT INTO Tickets VALUES
(1, 1, 'VIP', 5000),
(2, 2, 'Regular', 2000),
(3, 3, 'Regular', 1500),
(4, 4, 'VIP', 4000),
(5, 5, 'Regular', 2500);

-- PAYMENTS
INSERT INTO Payments VALUES
(1, 1, 5000, 'Credit Card', GETDATE()),
(2, 2, 2000, 'Easypaisa', GETDATE()),
(3, 3, 1500, 'Cash', GETDATE()),
(4, 4, 4000, 'Bank Transfer', GETDATE()),
(5, 5, 2500, 'JazzCash', GETDATE());


-- SELECT Queries

SELECT * FROM Attendee;
SELECT * FROM Organizers;
SELECT * FROM Venues;
SELECT * FROM Events;
SELECT * FROM Event_Registration;
SELECT * FROM Tickets;
SELECT * FROM Payments;

