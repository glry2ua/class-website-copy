## Class-website-copy

Python crawler that mirrors a website subtree to a local folder, including:
- HTML pages + linked assets (CSS/JS/images)
- Apache “Index of …” directories
- Extensionless files like Makefile for C compilation
- If class has updates run the script - it will skip the files you already have
- Please keep speed slow to be respectful of university servers

## Install
python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

## Update .py
in file mirror_cse101.py update url 

line 11 ROOT = "https://college_name.edu/prof_dir/class_dir/"

line 12 OUT_DIR = "Name_local_folder_for_the_copy"



## Run
python3 mirror_cse101.py

## Purpose
For fellow students who not always have reliable internet access with similar class structure
where files needed not always have extensions and are nested in multiple folders.

<img width="391" height="209" alt="Screenshot of the folder that contains: Makefile, Queue.c, Queue.h, QueueTest.c" src="https://github.com/user-attachments/assets/28011ade-45da-4012-9def-5ba8d123af8b" />

My class is CSE101, replace "cse101" inside of mirror_cse101.py with your class name.

<img width="306" height="243" alt="Screenshot 2026-04-05 at 7 32 50 PM" src="https://github.com/user-attachments/assets/8944aa87-0e29-4891-86c2-ec62bd709f06" />


Result looks like this

<img width="647" height="474" alt="Screenshot 2026-04-05 at 7 50 11 PM" src="https://github.com/user-attachments/assets/80c06e77-6f1c-4cdc-add2-b3b1f3cc1fe5" />
