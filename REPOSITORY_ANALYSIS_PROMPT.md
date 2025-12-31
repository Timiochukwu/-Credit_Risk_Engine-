# Repository Analysis Prompt for Tutorial Generation

Use this prompt to analyze any repository and generate a day-by-day tutorial guide.

---

## PROMPT TEMPLATE

```
Analyze this repository at [REPOSITORY_URL or PATH] and create a comprehensive day-by-day tutorial guide.

## Analysis Required:

1. **Repository Overview**
   - Project type and main technologies
   - Lines of code and complexity level
   - Current features and functionality

2. **File Structure**
   - Main application code location
   - Configuration files, tests, and documentation
   - Docker/deployment files and CI/CD setup

3. **Dependencies**
   - Production and development dependencies
   - Database and external service requirements
   - API integrations

4. **Complexity Assessment**
   - Skill level required (beginner/intermediate/advanced)
   - Estimated total time to build from scratch
   - Recommended tutorial length (X days)

## Output Format:

Provide a complete tutorial outline with:

**For each day, specify:**
- Day number and topic name
- Estimated time (1-2 hours per day)
- What you'll build (specific deliverable)
- Dependencies to install (ONLY for that day)
- Files to create
- Key concepts covered

**Structure guidelines:**
- Days 1-5: Foundation (setup, basic structure)
- Days 6-15: Core features
- Days 16-25: Advanced features & integrations
- Days 26-35: Production readiness (deployment, monitoring)
- Days 36+: Enterprise features (optional)

**Include:**
- Executive summary with complexity rating
- Complete day-by-day outline
- Dependency installation timeline (when to install what)
- Sample Day 001 guide (full example)

## Example Usage:

"I have a FastAPI repository at /path/to/project. Target audience: intermediate developers.
Time per day: 1-2 hours. Create a tutorial that starts with basic setup, builds features
incrementally, includes testing from day 1, and ends with production deployment."

Then request: "Build days 1-5", "Build days 6-10", etc.
```

---

**Result**: A structured tutorial that takes learners from zero to production-ready!
