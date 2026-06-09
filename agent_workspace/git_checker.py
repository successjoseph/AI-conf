import subprocess

# List of hardcoded git commands to check against
git_commands = [
    "make",
    "commit",
    "rebase",
    "push",
    "pull",
    "merge",
    "add",
    "remove",
    "branch",
    "checkout",
    "tag",
    "status"
]

# Function to execute git command
def execute_git_command(command):
    if command in git_commands:
        subprocess.run(["git", command])
    else:
        for key, value in git_commands_split.items():
            if command in value:
                subprocess.run(["git", key])

# Function to process human command
def process_human_command(human_command):
    words = human_command.lower().split()
    for word in words:
        execute_git_command(word)
        print(f"Executing: git {word}")

# Main function
def main():
    global git_commands_split
    git_commands_split = {
        "make": ["make"],
        "commit": ["make a commit", "commit"],
        "rebase": ["make a rebase", "rebase"],
        "push": ["push it now", "push"],
        "pull": ["pull the latest", "pull"],
        "merge": ["merge this branch", "merge"],
        "add": ["add the file", "add"],
        "remove": ["remove the file", "remove"],
        "branch": ["create a new branch", "branch"],
        "checkout": ["switch to branch", "checkout"],
        "tag": ["create a tag", "tag"],
        "status": ["check git status", "status"]
    }
    human_command = input("Enter your command: ")
    process_human_command(human_command)

if __name__ == "__main__":
    main()