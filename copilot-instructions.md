Important deployment reminder

- When you make runtime or server-side changes (for example `passenger_wsgi.py` or other files that the cPanel app uses), commit and push them to the repository so the remote/cPanel deployment can pull the latest code.

- Example git steps (run from the repository root):
  - git add passenger_wsgi.py copilot-instructions.md
  - git commit -m "passenger: delegate WSGI to passenger_wsgi_new and add deployment note"
  - git push origin pyinstaller-artifacts

Add this step to your deployment checklist so the web interface and any automated hooks pick up the change.

Note for the AI assistant: when making runtime/server edits, ensure the changes are committed to the active branch and pushed to the remote repository; offer to run the git push or provide exact commands when credentials are unavailable in the workspace.
