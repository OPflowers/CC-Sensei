import os
import subprocess


# rerun file until it finishes properly because the python buffer keeps running out of memory
def main():
    result = -1
    command = ["python3", "generate_videos_from_abr.py"]
    while result != 0:
        print(result)
        proc = subprocess.run(command, capture_output=True,)
        result = proc.returncode


if __name__ == "__main__":
    main()
