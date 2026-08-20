Mirrored copy of [henhouse](https://github.com/gmhoward9289-ops/henhouse) for CI.

GitHub Free orgs cannot grant `GITHUB_TOKEN` read access across private repos, so
pytest-session-trace installs this path in Actions instead of cloning henhouse.
Refresh when henhouse ships a release:

```powershell
Copy-Item C:\Users\gmhow\dev\henhouse\src vendor\henhouse\src -Recurse -Force
Copy-Item C:\Users\gmhow\dev\henhouse\pyproject.toml vendor\henhouse\ -Force
```
