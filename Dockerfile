FROM python:3.11

ENV APPLOCATION /bai

WORKDIR /app
COPY requirements.txt .

#Install necessary packages from requirements.txt with no cache dir allowing for installation on machine with very little memory on board
RUN pip install --upgrade pip
RUN pip --no-cache-dir install -r requirements.txt

COPY ./src ./src

#Exposing the default streamlit port
EXPOSE 8501

#Running the streamlit app
RUN echo "streamlit run --server.maxUploadSize=5 --server.baseUrlPath=$APPLOCATION src/app.py" > run_app.sh
ENTRYPOINT ["/bin/bash", "run_app.sh"]
