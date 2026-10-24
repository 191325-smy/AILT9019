-- Demo fixtures: 30 synthetic accounts, 15 in the HK cohort, 15 in SH.
-- Applied by seed.py right after schema.sql. Every account is a placeholder
-- contact - nothing here is a real person.
--
-- account ids are left to AUTOINCREMENT, so this file assumes an empty
-- accounts table (seed.py --reset guarantees that).

INSERT INTO accounts (username, password_hash) VALUES
('alice_chen', 'hash1'), ('bob_liu', 'hash2'), ('carol_wang', 'hash3'), ('david_zhao', 'hash4'), ('emma_sun', 'hash5'),
('frank_zhou', 'hash6'), ('grace_wu', 'hash7'), ('henry_xu', 'hash8'), ('ivy_huang', 'hash9'), ('jack_lin', 'hash10'),
('karen_he', 'hash11'), ('leo_gao', 'hash12'), ('mia_luo', 'hash13'), ('nathan_zheng', 'hash14'), ('olivia_liang', 'hash15'),
('peter_song', 'hash16'), ('queenie_tang', 'hash17'), ('ryan_feng', 'hash18'), ('sophia_cao', 'hash19'), ('tom_yao', 'hash20'),
('uma_pan', 'hash21'), ('victor_qin', 'hash22'), ('wendy_jiang', 'hash23'), ('xander_guo', 'hash24'), ('yuki_han', 'hash25'),
('zoe_shi', 'hash26'), ('aaron_deng', 'hash27'), ('bella_ma', 'hash28'), ('cody_lei', 'hash29'), ('diana_fan', 'hash30');

INSERT INTO profiles
(account_id, display_name, contact_info, city, preferred_role, languages, in_team) VALUES
(1,  'Alice Chen',  'alice@test.com',  'HK', 'Frontend',            '["Mandarin", "English"]', 0),
(2,  'Bob Liu',     'bob@test.com',    'HK', 'Backend',             '["English"]',             0),
(3,  'Carol Wang',  'carol@test.com',  'HK', 'Database',            '["Cantonese"]',           1),
(4,  'David Zhao',  'david@test.com',  'HK', 'Agentic Development', '["Mandarin", "English"]', 0),
(5,  'Emma Sun',    'emma@test.com',   'HK', 'Other',               '["Mandarin"]',            0),
(6,  'Frank Zhou',  'frank@test.com',  'HK', 'Frontend',            '["English", "Cantonese"]',0),
(7,  'Grace Wu',    'grace@test.com',  'HK', 'Backend',             '["Mandarin", "English"]', 0),
(8,  'Henry Xu',    'henry@test.com',  'HK', 'Database',            '["English"]',             0),
(9,  'Ivy Huang',   'ivy@test.com',    'HK', 'Agentic Development', '["Mandarin"]',            1),
(10, 'Jack Lin',    'jack@test.com',   'HK', 'Other',               '["Cantonese"]',           0),
(11, 'Karen He',    'karen@test.com',  'HK', 'Frontend',            '["Mandarin", "English"]', 0),
(12, 'Leo Gao',     'leo@test.com',    'HK', 'Backend',             '["English"]',             0),
(13, 'Mia Luo',     'mia@test.com',    'HK', 'Database',            '["Mandarin", "Cantonese"]',0),
(14, 'Nathan Zheng','nathan@test.com', 'HK', 'Agentic Development', '["English"]',             0),
(15, 'Olivia Liang','olivia@test.com', 'HK', 'Other',               '["Mandarin"]',            0),
(16, 'Peter Song',  'peter@test.com',  'SH', 'Frontend',            '["Mandarin", "English"]', 0),
(17, 'Queenie Tang','queenie@test.com','SH', 'Backend',             '["English"]',             0),
(18, 'Ryan Feng',   'ryan@test.com',   'SH', 'Database',            '["Mandarin"]',            0),
(19, 'Sophia Cao',  'sophia@test.com', 'SH', 'Agentic Development', '["Mandarin", "English"]', 0),
(20, 'Tom Yao',     'tom@test.com',    'SH', 'Other',               '["Cantonese"]',           1),
(21, 'Uma Pan',     'uma@test.com',    'SH', 'Frontend',            '["English"]',             0),
(22, 'Victor Qin',  'victor@test.com', 'SH', 'Backend',             '["Mandarin", "English"]', 0),
(23, 'Wendy Jiang', 'wendy@test.com',  'SH', 'Database',            '["Mandarin"]',            0),
(24, 'Xander Guo',  'xander@test.com', 'SH', 'Agentic Development', '["English", "Mandarin"]', 0),
(25, 'Yuki Han',    'yuki@test.com',   'SH', 'Other',               '["Cantonese"]',           0),
(26, 'Zoe Shi',     'zoe@test.com',    'SH', 'Frontend',            '["English"]',             0),
(27, 'Aaron Deng',  'aaron@test.com',  'SH', 'Backend',             '["Mandarin"]',            0),
(28, 'Bella Ma',    'bella@test.com',  'SH', 'Database',            '["English", "Mandarin"]', 0),
(29, 'Cody Lei',    'cody@test.com',   'SH', 'Agentic Development', '["Mandarin"]',            0),
(30, 'Diana Fan',   'diana@test.com',  'SH', 'Other',               '["English", "Cantonese"]',0);
