# Repository Analysis Prompt for Tutorial Generation

Use this prompt to analyze any repository and generate a comprehensive tutorial guide similar to the 40-45 day Credit Risk Engine tutorial.

---

## 📋 PROMPT TEMPLATE

```
I have a repository at [REPOSITORY_URL or LOCAL_PATH] and I want you to analyze it and create a comprehensive day-by-day tutorial guide similar to the 40-45 day structure.

Please perform the following analysis:

## 1. REPOSITORY OVERVIEW

First, analyze the repository structure:

**Task**: Explore the repository and provide:
- Project name and description
- Primary programming language(s)
- Main technologies/frameworks used
- Project type (web app, API, ML system, microservices, etc.)
- Current state (production, development, proof-of-concept)

**Commands to run**:
```bash
# List repository structure
ls -la

# Check for key files
find . -name "README*" -o -name "package.json" -o -name "requirements.txt" -o -name "Cargo.toml" -o -name "pom.xml" -o -name "go.mod"

# Count lines of code by language
find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.java" -o -name "*.go" | xargs wc -l

# Check git history
git log --oneline --all --graph | head -20
```

## 2. FILE STRUCTURE ANALYSIS

**Task**: Analyze the directory structure and identify:
- Main application code location (src/, app/, lib/, etc.)
- Configuration files
- Tests location
- Documentation
- Build/deployment files
- Database migrations (if any)
- Docker/containerization files
- CI/CD configurations

**Commands to run**:
```bash
# Show directory tree (limit depth to avoid overwhelm)
tree -L 3 -I 'node_modules|venv|__pycache__|.git'

# Or use find
find . -type d -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/venv/*' | head -50

# Check for configuration files
find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" -o -name "*.ini" | grep -v node_modules
```

## 3. DEPENDENCY ANALYSIS

**Task**: Identify all dependencies and their purposes:
- Production dependencies
- Development dependencies
- Database requirements
- External services needed
- API integrations

**Commands to run**:
```bash
# For Python
cat requirements.txt 2>/dev/null || cat pyproject.toml 2>/dev/null || cat Pipfile 2>/dev/null

# For Node.js
cat package.json 2>/dev/null | jq '.dependencies, .devDependencies'

# For Go
cat go.mod 2>/dev/null

# For Java
cat pom.xml 2>/dev/null || cat build.gradle 2>/dev/null

# Check for Docker
cat Dockerfile 2>/dev/null
cat docker-compose.yml 2>/dev/null
```

## 4. FUNCTIONALITY ANALYSIS

**Task**: Analyze what the code does:
- Main features/capabilities
- API endpoints (if applicable)
- Database models/schema
- Business logic components
- External integrations
- Background jobs/tasks

**Commands to run**:
```bash
# Find API routes/endpoints
grep -r "route\|endpoint\|@app\|@router\|@Get\|@Post" --include="*.py" --include="*.js" --include="*.ts" | head -20

# Find database models
grep -r "class.*Model\|Table\|Schema" --include="*.py" | head -20

# Find main entry points
find . -name "main.*" -o -name "app.*" -o -name "server.*" -o -name "index.*"

# Check for tests
find . -path "*/test*" -name "*.py" -o -path "*/test*" -name "*.js" | wc -l
```

## 5. COMPLEXITY ASSESSMENT

**Task**: Determine the complexity level:
- Beginner, Intermediate, or Advanced?
- Estimated time to build from scratch
- Number of distinct components
- Integration complexity
- DevOps complexity

**Analysis factors**:
- Lines of code (< 5k = simple, 5-20k = medium, > 20k = complex)
- Number of dependencies
- Infrastructure requirements
- Database complexity
- API integrations
- Testing coverage
- Deployment complexity

## 6. LEARNING PATH STRUCTURE

**Task**: Based on the analysis, propose a day-by-day tutorial structure:

For each day, specify:
- **Day X**: [Topic Name]
- **Estimated time**: X-X hours
- **What you'll build**: [Specific deliverable]
- **Prerequisites**: [What must be done first]
- **Key concepts**: [What learner will understand]
- **Dependencies to install**: [Specific packages for this day]
- **Files to create**: [List of files]

**Structure guidelines**:
- Days 1-5: Foundation (setup, basic structure)
- Days 6-15: Core features (main functionality)
- Days 16-25: Advanced features & integrations
- Days 26-35: Production readiness (deployment, monitoring)
- Days 36-40: Optional advanced topics
- Days 41-45: Enterprise features (if applicable)

## 7. INCREMENTAL DEPENDENCY INSTALLATION

**Task**: Map dependencies to specific days:

For each day, list ONLY the dependencies needed:
```
Day 1: python, virtualenv
Day 2: fastapi, uvicorn
Day 3: sqlalchemy, psycopg2
...etc
```

## 8. TARGET AUDIENCE

**Task**: Define the target audience:
- Skill level (beginner, intermediate, advanced)
- Required prerequisites
- Estimated total time to complete
- Learning outcomes

## 9. TUTORIAL OUTLINE

**Task**: Generate a complete tutorial outline:

```markdown
# [Project Name] - XX-Day Tutorial

## Days 001-005: Foundation
- Day 001: [Topic]
- Day 002: [Topic]
...

## Days 006-010: [Category]
- Day 006: [Topic]
...

[Continue for all days]
```

## 10. SAMPLE DAY TEMPLATE

**Task**: Generate a complete example for Day 001:

Include:
- Estimated time
- What you'll build today
- Why this topic matters
- Prerequisites
- Part-by-part breakdown
- Code examples
- Testing section
- Verification checklist
- What you've accomplished
- Key takeaways
- Next steps
- Files created
- Commands reference

---

## OUTPUT FORMAT

Please provide your analysis in this structure:

1. **Executive Summary** (1 paragraph)
2. **Repository Statistics** (table format)
3. **Technology Stack** (bulleted list)
4. **Complexity Assessment** (rating + justification)
5. **Recommended Tutorial Length** (X days, X hours total)
6. **Complete Day-by-Day Outline** (all days listed)
7. **Dependency Timeline** (when to install what)
8. **Sample Day 001 Guide** (full example)

---

## EXAMPLE USAGE

Replace the placeholders and run:

```
I have a repository at https://github.com/user/project and I want you to analyze it and create a comprehensive day-by-day tutorial guide.

[Paste full prompt template above]
```

---

## FOLLOW-UP QUESTIONS

After initial analysis, you can ask:

1. "Create guides for days 1-5"
2. "Create guides for days 6-10"
3. "Generate the complete tutorial structure as markdown files"
4. "What's the estimated difficulty for an intermediate developer?"
5. "Break down day X into more detail"
6. "Show me the complete dependency installation timeline"

---

## TIPS FOR BEST RESULTS

1. **Provide context**: If you know the project's purpose, mention it
2. **Specify skill level**: "Create this for intermediate developers"
3. **Set time constraints**: "Each day should be 1-2 hours maximum"
4. **Request format**: "Generate as markdown files ready to commit"
5. **Incremental approach**: "Start with days 1-5, I'll review before continuing"

---

## WHAT THE AI WILL ANALYZE

The AI will automatically:
- ✅ Read all files in the repository
- ✅ Understand code structure and patterns
- ✅ Identify dependencies and their purposes
- ✅ Determine complexity level
- ✅ Map features to tutorial days
- ✅ Create logical learning progression
- ✅ Generate complete code examples
- ✅ Include testing and deployment
- ✅ Provide verification steps

---

## EXPECTED DELIVERABLES

After using this prompt, you'll receive:

1. **Complete analysis report**
2. **Day-by-day tutorial outline** (XX days)
3. **Dependency installation schedule**
4. **Sample day guide** (Day 001 fully written)
5. **Estimated time commitment**
6. **Complexity rating**
7. **Prerequisites list**
8. **Learning outcomes**

Then you can request:
- "Build days 1-5"
- "Build days 6-10"
- etc.

---

## CUSTOMIZATION OPTIONS

You can modify the prompt to:

```
"Create a 20-day tutorial instead of 40"
"Focus only on backend, skip frontend"
"Include Docker from day 1"
"Make it suitable for beginners"
"Each day should be 30 minutes maximum"
"Include Kubernetes deployment"
"Add CI/CD from the start"
"Focus on testing and TDD"
```

---

## QUALITY CHECKLIST

Ensure the AI's output includes:

- [ ] Clear day-by-day structure
- [ ] Realistic time estimates
- [ ] Incremental complexity
- [ ] Dependencies per day (not all at once)
- [ ] Complete code examples
- [ ] Testing strategies
- [ ] Verification steps
- [ ] Troubleshooting sections
- [ ] Best practices
- [ ] Production considerations

---

## SAVE THIS PROMPT

Save this file as `REPOSITORY_ANALYSIS_PROMPT.md` for future use!

```bash
# Example usage in shell
cat REPOSITORY_ANALYSIS_PROMPT.md

# Use with Claude Code or any AI assistant
# Copy and paste the prompt, replacing [REPOSITORY_URL]
```

---

## SUCCESS INDICATORS

You'll know the analysis is good when:

1. ✅ Each day builds on the previous
2. ✅ Time estimates are realistic (1-2 hours per day)
3. ✅ Dependencies are introduced incrementally
4. ✅ Code examples are complete and runnable
5. ✅ Testing is included from early days
6. ✅ Deployment covered in later days
7. ✅ Each day has clear deliverables
8. ✅ Complexity increases gradually

---

## SUPPORT

If the analysis seems off:

1. **Provide more context**: "This is a microservices architecture"
2. **Specify what's important**: "Focus on the ML pipeline"
3. **Clarify audience**: "Make it for people who know Python but not ML"
4. **Adjust scope**: "Skip the frontend, backend only"
5. **Request refinement**: "Day 5 seems too complex, can you split it?"

---

## FINAL NOTE

This prompt template is designed to work with:
- ✅ Claude Code
- ✅ Claude 3.5 Sonnet
- ✅ Claude Opus
- ✅ Any AI with code analysis capabilities

**Result**: A comprehensive, structured tutorial that takes learners from zero to production-ready!

🚀 **Happy Tutorial Creating!**
```

---

## Quick Start Example

Here's a complete example ready to use:

```
I have a repository at /path/to/my/project and I want you to create a 30-day tutorial guide for it.

The project is a FastAPI-based e-commerce API with PostgreSQL database.

Target audience: Intermediate Python developers
Time per day: 1-2 hours
Focus: Backend only (no frontend)

Please analyze the repository structure, identify all components, and create a day-by-day tutorial that:
1. Starts with basic setup
2. Builds features incrementally
3. Includes testing from day 1
4. Ends with production deployment
5. Installs dependencies only when needed (per day)

[Rest of analysis template from above]
```

---

**Use this prompt template to create comprehensive tutorials for ANY repository!** 📚🚀
