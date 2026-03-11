# learning-services

##  Contribution Guidelines & Git Workflow

To maintain high code quality and avoid merge conflicts, all team members **MUST** strictly follow these rules:

### 1. Branching Strategy

- **`main`**: Production-ready code ONLY. Direct pushes are blocked.
- **`develop`**: The integration branch. All feature branches must branch off from here and merge back here.
- **Feature Branches**: When picking up a task, create a branch from `develop` using the following naming convention:
  - `feat/feature-name` (e.g., `feat/pdf-extraction`)
  - `fix/bug-name` (e.g., `fix/db-connection`)
  - `chore/task-name` (e.g., `chore/update-dependencies`)
  - `docs/document-name` (e.g., `docs/api-endpoints`)

### 2. Commits

Use descriptive, conventional commit messages:
- ✅ `feat: add Tavily web search integration`
- ✅ `fix: handle empty pdf files during extraction`
- ✅ `chore: update requirements.txt`
- ❌ `fixed bug` or `updated files` or `done`

### 3. Pull Requests (PRs)

- **Direct pushes to `main` or `develop` are BLOCKED.**
- Push your feature branch to GitHub and open a Pull Request against the `develop` branch.
- Fill out the provided PR Template.
- Wait for at least **1 Approval** (from the Team Lead) before merging.
- Ensure your code doesn't break existing functionality before requesting a review.

