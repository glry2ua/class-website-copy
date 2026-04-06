# class-website-copy

Python crawler that mirrors a website subtree to a local folder, including:
- HTML pages + linked assets (CSS/JS/images)
- Apache “Index of …” directories
- Extensionless files like Makefile, Holmes, Small

## Install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

## Run
python mirror_cse101.py --root "https://people.ucsc.edu/~ptantalo/cse101/" --out "CSE101_mirror" --resume
