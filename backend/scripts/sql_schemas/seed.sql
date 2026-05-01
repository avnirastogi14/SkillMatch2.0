
-- CLEAN START

TRUNCATE role_technologies;
TRUNCATE technologies CASCADE;


-- TECHNOLOGIES

INSERT INTO technologies (name) VALUES
('python'), ('java'), ('c++'), ('javascript'),
('sql'), ('react'), ('node.js'),
('docker'), ('kubernetes'),
('aws'), ('gcp'), ('azure'),
('linux'), ('git'),
('rest api'), ('microservices'),
('mongodb'), ('postgresql'),
('tensorflow'), ('pytorch'),
('pandas'), ('numpy'),
('spark'), ('hadoop'), ('airflow'), ('kafka'),
('cybersecurity'), ('networking'),
('system design'), ('embedded c'), ('firmware'),
('nlp'), ('computer vision'),
('devops'), ('ci/cd'), ('terraform');


-- CYBERSECURITY

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name = 'cybersecurity'
WHERE d.track = 'cybersecurity';


-- NETWORKING

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name = 'networking'
WHERE d.track = 'networking';


-- FRONTEND

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('react', 'javascript')
WHERE d.track = 'frontend';


-- BACKEND

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('python', 'java', 'sql', 'rest api', 'microservices')
WHERE d.track = 'backend';


-- FULLSTACK

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('python', 'react', 'javascript')
WHERE d.track = 'fullstack';


-- DATA ENGINEERING

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('spark', 'hadoop', 'airflow', 'kafka')
WHERE d.track = 'data_engineering';


-- DATA SCIENCE

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('python', 'pandas', 'numpy', 'sql')
WHERE d.track = 'data_science';


-- AI / ML

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('tensorflow', 'pytorch', 'nlp', 'computer vision')
WHERE d.track = 'ai_ml';


-- CLOUD / DEVOPS

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('docker', 'kubernetes', 'aws', 'terraform', 'ci/cd')
WHERE d.track = 'cloud_devops';


-- SYSTEMS

INSERT INTO role_technologies (role_id, tech_id)
SELECT r.id, t.id
FROM dynamic_it_roles d
JOIN roles r ON LOWER(d.title) = LOWER(r.title)
JOIN technologies t ON t.name IN ('system design', 'embedded c', 'firmware')
WHERE d.track = 'systems';