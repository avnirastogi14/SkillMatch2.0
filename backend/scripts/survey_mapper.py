def map_survey_to_profile(answers):
    profile = {
        "skills": [],
        "technologies": [],
        "interests": []
    }

    
    # SECTION 1 — SKILLS
    
    profile["skills"].extend(answers.get("languages", []))

    if answers.get("strong_language_rating", 0) >= 4:
        profile["skills"].append("programming")

    profile["technologies"].extend(answers.get("technologies", []))

    
    # SECTION 2 — INTERESTS
    
    interest_map = {
        "Building features": ["frontend", "backend"],
        "Optimizing systems": ["backend", "cloud_devops"],
        "Analyzing data": ["data_science", "ai_ml"],
        "Designing scalable systems": ["backend", "systems"],

        "Logical/DSA": ["backend"],
        "Real-world applications": ["fullstack"],
        "Data-heavy problems": ["data_science", "ai_ml"],
        "System design": ["backend", "cloud_devops"],

        "Build scalable systems": ["backend"],
        "Improve UI/UX": ["frontend"],
        "Work with data insights": ["data_science", "ai_ml"],
        "Ensure security": ["cybersecurity"],
    }

    for answer in answers.get("interest_answers", []):
        profile["interests"].extend(interest_map.get(answer, []))

    
    # SECTION 3 — WORK STYLE (optional signals)
    
    if answers.get("learning_preference") == "Build projects":
        profile["skills"].append("practical development")

    
    # SECTION 4 — EXPERIENCE SIGNALS
    
    exp_map = {
        "Static websites": ["html", "css"],
        "Full-stack apps": ["api", "database", "frontend"],
        "APIs / Backend systems": ["api", "backend"],
        "AI/ML projects": ["machine learning", "python"],
    }

    exp = answers.get("experience")
    if exp in exp_map:
        profile["skills"].extend(exp_map[exp])

    profile["technologies"].extend(answers.get("worked_with", []))

    
    # SECTION 5 — DOMAIN (VERY IMPORTANT)
    
    domain_map = {
        "Web Development": ["frontend", "backend", "fullstack"],
        "AI / Machine Learning": ["ai_ml", "data_science"],
        "Cloud / DevOps": ["cloud_devops"],
        "Cybersecurity": ["cybersecurity"],
        "Data Engineering": ["data_engineering"]
    }

    domain = answers.get("domain_interest")
    if domain in domain_map:
        profile["interests"].extend(domain_map[domain])

    
    # CLEANUP
    
    profile["skills"] = list(set(profile["skills"]))
    profile["technologies"] = list(set(profile["technologies"]))
    profile["interests"] = list(set(profile["interests"]))

    return profile