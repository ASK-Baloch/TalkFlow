import os
import subprocess

commits = [
    {
        "files": ["services/recording-worker/app/types.py", "services/recording-worker/app/config.py"],
        "msg": "feat(recording): add types and config"
    },
    {
        "files": ["services/recording-worker/app/call_id.py", "services/recording-worker/app/validator.py"],
        "msg": "feat(recording): add validation logic"
    },
    {
        "files": ["services/recording-worker/app/source.py"],
        "msg": "feat(recording): add SFTP source handling"
    },
    {
        "files": ["services/recording-worker/app/repository.py"],
        "msg": "feat(recording): add postgres repository"
    },
    {
        "files": ["services/recording-worker/app/events.py"],
        "msg": "feat(recording): add kafka event consumer"
    },
    {
        "files": ["services/recording-worker/app/processor.py"],
        "msg": "feat(recording): add job processor"
    },
    {
        "files": ["services/recording-worker/app/main.py", "services/recording-worker/app/__init__.py"],
        "msg": "feat(recording): add main entrypoint"
    },
    {
        "files": ["services/recording-worker/Dockerfile", "services/recording-worker/requirements.txt", "services/recording-worker/.gitignore", "services/recording-worker/pytest.ini"],
        "msg": "chore(recording): add docker and testing setup"
    },
    {
        "files": ["services/ai-gateway/app/realtime/recording/"],
        "msg": "feat(ai-gateway): add recording publisher"
    },
    {
        "files": ["services/ai-gateway/alembic/", "services/ai-gateway/alembic.ini"],
        "msg": "feat(ai-gateway): add recording database migrations"
    },
    {
        "files": ["services/ai-gateway/app/core/", "services/ai-gateway/app/main.py", "services/ai-gateway/app/realtime/audiosocket/server.py", "services/ai-gateway/requirements.txt", "services/ai-gateway/Dockerfile"],
        "msg": "feat(ai-gateway): integrate recording events"
    },
    {
        "files": ["docs/phases/", "docs/adr/", "PROJECT_CONTEXT.md"],
        "msg": "docs: add phase 11 adrs and project context"
    },
    {
        "files": ["docs/ARCHITECTURE.md", "docs/BENCHMARKS.md", "docs/CURRENT_STATUS.md", "docs/ROADMAP.md", "docs/SECURITY.md", "docs/TESTING.md"],
        "msg": "docs: update master documentation for phase 11"
    },
    {
        "files": ["tools/", "services/tts-worker/"],
        "msg": "chore: format tools and tts-worker"
    },
    {
        "files": ["scripts/", "investigate_audio.py", "timeline_parser.py", "docker-compose.yml", ".env.example", ".gitignore", ".github/"],
        "msg": "chore: format scripts and update ci/docker"
    }
]

for commit in commits:
    for f in commit["files"]:
        subprocess.run(["git", "add", f], check=True)
    subprocess.run(["git", "commit", "-m", commit["msg"]], check=True)

# Add any remaining files that were missed to the last commit
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "--amend", "--no-edit"], check=True)

print("Done creating 15 commits.")
