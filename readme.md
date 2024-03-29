![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://beyondallinfo.streamlit.app/)



# Beyond All Information

Get your stats of Beyond All Reason https://www.beyondallreason.info/.

- https://beyondallinfo.streamlit.app/
- https://bai.furyhawk.lol/


## Run locally

### Docker
```sh
docker build -t bai .
docker run -p 8501:80 bai
```
#### Docker compose
```sh
docker compose build
docker compose up -d
```

http://localhost:8501/bai


## DEV env

- Python >= `3.11`
- Packages included in `requirements.txt` file
- (Anaconda for easy installation)

### Python virtual env setup
For local setup, I recommend to use [Miniconda](https://docs.conda.io/en/latest/miniconda.html), a minimal version of the popular [Anaconda](https://www.anaconda.com/) distribution that contains only the package manager `conda` and Python. Follow the installation instructions on the [Miniconda Homepage](https://docs.conda.io/en/latest/miniconda.html).

After installation of Anaconda/Miniconda, run the following command(s) from the project directory:

### Install dependencies
Conda virtual environment:
```sh
conda create --name myenv python=3.11
conda activate myenv
conda install --file requirements.txt -c conda-forge
```

As **Conda has limited package support for python 3.11** activate your virtual environment **then** install the dependencies using

```sh
pip install -r requirements.txt
```
