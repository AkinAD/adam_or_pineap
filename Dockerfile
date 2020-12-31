FROM python:3.6-slim
# copy all the files to the container in folder called deploy
COPY . /deploy/ 

# set a directory for the app
WORKDIR /deploy/

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# tell the port number the container should expose
EXPOSE 80

# run the command
# CMD ["python", "./app.py"]
ENTRYPOINT ["flask", "run", "-h", "0.0.0.0", "-p", "80"]
