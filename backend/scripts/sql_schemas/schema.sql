-- SKILLMATCH 2.0 DATABASE SCHEMA (POSTGRES)
-- O*NET + SURVEY + MATCHING ENGINE

-- DROP (for reset)
DROP TABLE IF EXISTS role_match_scores CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS user_responses CASCADE;
DROP TABLE IF EXISTS survey_options CASCADE;
DROP TABLE IF EXISTS survey_questions CASCADE;

DROP TABLE IF EXISTS role_technologies CASCADE;
DROP TABLE IF EXISTS role_knowledge CASCADE;
DROP TABLE IF EXISTS role_skills CASCADE;

DROP TABLE IF EXISTS technologies CASCADE;
DROP TABLE IF EXISTS knowledge CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- ROLES (IT ONLY)
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    onet_code VARCHAR(10) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'IT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ROLE ALIASES (from alternate_titles.txt)
CREATE TABLE role_aliases (
    id SERIAL PRIMARY KEY,
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    alias TEXT NOT NULL
);

CREATE INDEX idx_role_aliases_role ON role_aliases(role_id);
CREATE INDEX idx_role_aliases_alias ON role_aliases(alias);

CREATE INDEX idx_roles_onet_code ON roles(onet_code);

-- SKILLS
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    type TEXT DEFAULT 'technical'
);

-- KNOWLEDGE (DSA, OS, DBMS, etc.)
CREATE TABLE knowledge (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- TECHNOLOGIES (TOOLS / STACKS)
CREATE TABLE technologies (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- ROLE ↔ SKILLS
CREATE TABLE role_skills (
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(id) ON DELETE CASCADE,
    importance FLOAT,
    level FLOAT,
    PRIMARY KEY (role_id, skill_id)
);

CREATE INDEX idx_role_skills_role ON role_skills(role_id);
CREATE INDEX idx_role_skills_skill ON role_skills(skill_id);

-- ROLE ↔ KNOWLEDGE
CREATE TABLE role_knowledge (
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    knowledge_id INT REFERENCES knowledge(id) ON DELETE CASCADE,
    importance FLOAT,
    level FLOAT,
    PRIMARY KEY (role_id, knowledge_id)
);

-- ROLE ↔ TECHNOLOGIES
CREATE TABLE role_technologies (
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    tech_id INT REFERENCES technologies(id) ON DELETE CASCADE,
    demand BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (role_id, tech_id)
);

-- SURVEY QUESTIONS
CREATE TABLE survey_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    category TEXT CHECK (category IN ('skills', 'interest', 'experience')),
    weight FLOAT DEFAULT 1.0
);

-- SURVEY OPTIONS
CREATE TABLE survey_options (
    id SERIAL PRIMARY KEY,
    question_id INT REFERENCES survey_questions(id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    score FLOAT NOT NULL
);

-- USER RESPONSES
CREATE TABLE user_responses (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    question_id INT REFERENCES survey_questions(id),
    option_id INT REFERENCES survey_options(id)
);

-- USER PROFILE (DERIVED)
CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    skill_score JSONB,
    interest_score JSONB,
    knowledge_score JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ROLE MATCH SCORES
CREATE TABLE role_match_scores (
    user_id INT,
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    score FLOAT,
    PRIMARY KEY (user_id, role_id)
);

-- OPTIONAL: ROLE TAGS (FOR BETTER UX)
CREATE TABLE role_tags (
    id SERIAL PRIMARY KEY,
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    tag TEXT
);

-- USEFUL INDEXES
CREATE INDEX idx_roles_title ON roles USING GIN (to_tsvector('english', title));
CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_tech_name ON technologies(name);