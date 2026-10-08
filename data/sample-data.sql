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
