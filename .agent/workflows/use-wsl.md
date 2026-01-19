---
description: Always use WSL Ubuntu shell for commands
---

// turbo-all
1. Identify the command to run.
2. Wrap the command in the WSL bridge:
   ```bash
   wsl -d Ubuntu-22.04 bash -c "<command>"
   ```
3. Ensure absolute paths are converted if necessary, or execute from the project root.
