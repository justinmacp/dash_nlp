#Description

This project implements a dashboard showing relevant topics on today's news.

The project uses the following tools:
* Python 3.7
* dash (flask) for the dashboard implementation
* sklearn LDA for topic analysis
* Beautifulsoup for webcrawling
* Docker for containerization
* mySQL for RMDB (doesn't work with python 3.8 or 3.9)

use nomkl versions of the following libraries:

    conda install nomkl numpy scipy scikit-learn numexpr
    conda remove mkl mkl-service