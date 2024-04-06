### Steps for Steps
* Clone the git repository:
  - `git clone <url-of-git-repo>`
* Setup virtual environment for development:
  - `python -m venv <name-of-virtual-env>`
* Activate virtual environment
  - `<name-of-virtual-env>/scripts/activate`
* Install the required dependencies
  - `pip install -r requirements.txt`
* Run the api in localhost:
  - `uvicorn app:app --reload`