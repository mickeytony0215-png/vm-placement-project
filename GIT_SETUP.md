# Git Setup Instructions

## Initial Repository Setup

### 1. Initialize Git Repository

```bash
cd vm-placement-project
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: VM Placement Project structure

- Project structure with src, data, results, tests directories
- Implemented FFD, BFD, NLP, and RLS-FFD algorithms
- Added VM and PM generators
- Added evaluation metrics
- Comprehensive README and documentation"
```

### 4. Create GitHub Repository

Go to GitHub and create a new repository named `vm-placement-project`

### 5. Add Remote and Push

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR-USERNAME/vm-placement-project.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Create Development Branch

```bash
git checkout -b develop
git push -u origin develop
```

## Workflow for Team Members

### Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/vm-placement-project.git
cd vm-placement-project
```

### Create Feature Branch

```bash
# Make sure you're on develop branch
git checkout develop

# Pull latest changes
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Work on Feature

```bash
# Make changes
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat(scope): description of changes"

# Push to GitHub
git push -u origin feature/your-feature-name
```

### Create Pull Request

1. Go to GitHub repository
2. Click "Compare & pull request"
3. Set base branch to `develop`
4. Add description
5. Request review from team members
6. Merge after approval

## Useful Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline --graph

# Switch branches
git checkout branch-name

# Update current branch with latest changes
git pull

# View differences
git diff

# Undo uncommitted changes
git checkout -- filename

# Create and switch to new branch
git checkout -b new-branch-name
```

## Branch Strategy Summary

```
main (production-ready code)
  |
  └── develop (development branch)
       |
       ├── feature/stage1-literature
       ├── feature/stage2-nlp
       ├── feature/stage2-ffd-bfd
       ├── feature/stage2-rls-ffd
       ├── feature/stage3-experiments
       └── feature/stage4-documentation
```

## Commit Message Guidelines

**Format:** `<type>(<scope>): <subject>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance

**Examples:**
```
feat(ffd): implement First Fit Decreasing algorithm
fix(metrics): correct energy consumption calculation
docs(readme): add installation instructions
test(bfd): add unit tests for Best Fit Decreasing
refactor(utils): improve VM generator efficiency
chore(deps): update numpy to 1.24.0
```

---

For more details, see `docs/contributing.md`
