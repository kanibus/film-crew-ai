# 📤 Publishing Film Crew AI to GitHub

## For Repository Owner Only

### Step 1: Authenticate GitHub CLI
```bash
setup-github.bat
```
Choose browser authentication when prompted.

### Step 2: Create and Push Repository
```bash
create-github-repo.bat
```

This will:
- Create a public repository named `film-crew-ai`
- Push all code to GitHub
- Provide the repository URL

### Step 3: Update README Links

After creating the repository, update these placeholders in `README.md`:
- Replace `[repository-owner]` with your GitHub username
- Replace `yourusername` in issue/feature request links
- Update Discord link if you have a server

### Step 4: Add Repository Topics

On GitHub, go to Settings → Topics and add:
- `ai`
- `video-generation`
- `google-veo3`
- `claude`
- `film-production`
- `screenplay`
- `prompt-engineering`

### Step 5: Create Initial Release (Optional)

```bash
gh release create v1.0.0 --title "Film Crew AI v1.0.0" --notes "Initial release with 8 specialized film production agents"
```

---

## For Users

Users should simply clone the repository:

```bash
git clone https://github.com/[your-username]/film-crew-ai.git
cd film-crew-ai
install-film-crew.bat
```

They do NOT need to:
- Create their own repository
- Run create-github-repo.bat
- Set up GitHub authentication (unless contributing)

The system works locally after installation!