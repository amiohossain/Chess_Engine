import subprocess
import datetime as dt

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def main():
    commit_message = f"Updated Time : {dt.datetime.now()}"
    run_command("git add .")
    run_command(f'git commit -m "{commit_message}"')
    run_command("git push")

if __name__ == "__main__":
    main()