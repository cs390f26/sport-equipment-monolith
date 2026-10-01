-- Sample data for MySQL.
-- use this for seeding and automated tests.
-- total is the amount owned. Available is total minus open ticket quantities for that equipment.

CREATE TABLE Equipment (
  equipmentId VARCHAR(32) PRIMARY KEY,
  itemName VARCHAR(64) NOT NULL,
  total INT NOT NULL
);

CREATE TABLE Ticket (
  ticketId VARCHAR(32) PRIMARY KEY,
  createdAt VARCHAR(30) NOT NULL,
  name VARCHAR(64) NOT NULL,
  quantity INT NOT NULL,
  equipmentId VARCHAR(32) NOT NULL,
  FOREIGN KEY (equipmentId) REFERENCES Equipment(equipmentId)
);


-- 1. Browse equipment
-- Each item shows available/total. Bats 0/2, Helmets 9/10, Baseballs 21/24.

INSERT INTO Equipment (equipmentId, itemName, total) VALUES
  ('k7m1xq9p', 'Bats', 2),
  ('g4n8kp2w', 'Gloves', 12),
  ('h2p6rt3c', 'Helmets', 10),
  ('b9q4vs1b', 'Baseballs', 24),
  ('c2t7yh5d', 'Catcher''s gear', 3),
  ('a8w3mn4f', 'Bases', 4);

INSERT INTO Ticket (ticketId, createdAt, name, quantity, equipmentId) VALUES
  ('n4p8wd2c', '2026-08-03T14:30:00.000Z', 'Maya', 1, 'h2p6rt3c'),
  ('t9r3ab6k', '2026-07-30T16:00:00.000Z', 'Jordan', 3, 'b9q4vs1b'),
  ('k7m2xq9p', '2026-07-28T12:15:00.000Z', 'Lucas', 2, 'k7m1xq9p');


-- 2. Add equipment
-- Softball gloves are added with a total of 12.
-- Available and total are both 12. Other rows are unchanged from scenario 1.

INSERT INTO Equipment (equipmentId, itemName, total) VALUES
  ('k7m1xq9p', 'Bats', 2),
  ('g4n8kp2w', 'Gloves', 12),
  ('h2p6rt3c', 'Helmets', 10),
  ('b9q4vs1b', 'Baseballs', 24),
  ('c2t7yh5d', 'Catcher''s gear', 3),
  ('a8w3mn4f', 'Bases', 4),
  ('s6f2gl8q', 'Softball gloves', 12);

INSERT INTO Ticket (ticketId, createdAt, name, quantity, equipmentId) VALUES
  ('n4p8wd2c', '2026-08-03T14:30:00.000Z', 'Maya', 1, 'h2p6rt3c'),
  ('t9r3ab6k', '2026-07-30T16:00:00.000Z', 'Jordan', 3, 'b9q4vs1b'),
  ('k7m2xq9p', '2026-07-28T12:15:00.000Z', 'Lucas', 2, 'k7m1xq9p');


-- 3. View open tickets
-- Pressing Bats lists only Lucas, quantity 2.
-- Same table contents as scenario 1.

INSERT INTO Equipment (equipmentId, itemName, total) VALUES
  ('k7m1xq9p', 'Bats', 2),
  ('g4n8kp2w', 'Gloves', 12),
  ('h2p6rt3c', 'Helmets', 10),
  ('b9q4vs1b', 'Baseballs', 24),
  ('c2t7yh5d', 'Catcher''s gear', 3),
  ('a8w3mn4f', 'Bases', 4);

INSERT INTO Ticket (ticketId, createdAt, name, quantity, equipmentId) VALUES
  ('n4p8wd2c', '2026-08-03T14:30:00.000Z', 'Maya', 1, 'h2p6rt3c'),
  ('t9r3ab6k', '2026-07-30T16:00:00.000Z', 'Jordan', 3, 'b9q4vs1b'),
  ('k7m2xq9p', '2026-07-28T12:15:00.000Z', 'Lucas', 2, 'k7m1xq9p');


-- 4. Successful create ticket
-- Alex borrows 1 Gloves. Gloves total stays 12. Available goes from 12 to 11.
-- Other equipment rows are unchanged from scenario 1.

INSERT INTO Equipment (equipmentId, itemName, total) VALUES
  ('k7m1xq9p', 'Bats', 2),
  ('g4n8kp2w', 'Gloves', 12),
  ('h2p6rt3c', 'Helmets', 10),
  ('b9q4vs1b', 'Baseballs', 24),
  ('c2t7yh5d', 'Catcher''s gear', 3),
  ('a8w3mn4f', 'Bases', 4);

INSERT INTO Ticket (ticketId, createdAt, name, quantity, equipmentId) VALUES
  ('m3n8kp2w', '2026-08-05T10:00:00.000Z', 'Alex', 1, 'g4n8kp2w'),
  ('n4p8wd2c', '2026-08-03T14:30:00.000Z', 'Maya', 1, 'h2p6rt3c'),
  ('t9r3ab6k', '2026-07-30T16:00:00.000Z', 'Jordan', 3, 'b9q4vs1b'),
  ('k7m2xq9p', '2026-07-28T12:15:00.000Z', 'Lucas', 2, 'k7m1xq9p');


-- 5. Open a ticket to return
-- Get ticket k7m2xq9p by id. Tables are otherwise the same as scenario 1.

INSERT INTO Equipment (equipmentId, itemName, total) VALUES
  ('k7m1xq9p', 'Bats', 2);

INSERT INTO Ticket (ticketId, createdAt, name, quantity, equipmentId) VALUES
  ('k7m2xq9p', '2026-07-28T12:15:00.000Z', 'Lucas', 2, 'k7m1xq9p');


-- 6. Return item
-- Lucas returns 2 Bats. Ticket k7m2xq9p is deleted.
-- Bats total stays 2. Available goes from 0 to 2.

INSERT INTO Equipment (equipmentId, itemName, total) VALUES
  ('k7m1xq9p', 'Bats', 2),
  ('g4n8kp2w', 'Gloves', 12),
  ('h2p6rt3c', 'Helmets', 10),
  ('b9q4vs1b', 'Baseballs', 24),
  ('c2t7yh5d', 'Catcher''s gear', 3),
  ('a8w3mn4f', 'Bases', 4);

INSERT INTO Ticket (ticketId, createdAt, name, quantity, equipmentId) VALUES
  ('n4p8wd2c', '2026-08-03T14:30:00.000Z', 'Maya', 1, 'h2p6rt3c'),
  ('t9r3ab6k', '2026-07-30T16:00:00.000Z', 'Jordan', 3, 'b9q4vs1b');