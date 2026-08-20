# PyPI trusted publishing (one-time)

Register a **pending publisher** at https://pypi.org/manage/account/publishing/
before `release.yml` can upload.

| Field | Value |
| --- | --- |
| Owner | `gmhoward9289-ops` |
| Repository | `pytest-session-trace` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

GitHub: **Settings → Environments → `pypi`** (no secrets; OIDC only).

`pytest-session-trace` depends on **henhouse** on PyPI — register and publish
henhouse first, then this package.

Re-run after setup:

```powershell
gh workflow run release -R gmhoward9289-ops/pytest-session-trace --ref v0.1.1
```

See also [henhouse/docs/PYPI-SETUP.md](https://github.com/gmhoward9289-ops/henhouse/blob/main/docs/PYPI-SETUP.md).
