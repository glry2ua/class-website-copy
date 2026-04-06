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

## Run
python mirror_cse101.py --root "https://insertfullpathhere.edu/professor/classfolder/" --out "Yourcopyfoldername_mirror" --resume

## Purpose
For fellow students who not always have reliable internet access with similar class structure
where files needed not always have extensions and are nested in multiple folders.

<img width="391" height="209" alt="Screenshot of the folder that contains: Makefile, Queue.c, Queue.h, QueueTest.c" src="https://github.com/user-attachments/assets/28011ade-45da-4012-9def-5ba8d123af8b" />
