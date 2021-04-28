FROM bnsdcr/bcfm-buse-python-flask-api:base-image-python3 


WORKDIR /flask-api
COPY . .

#EXPOSE 9095

CMD ["python3", "task.py"]
#ENTRYPOINT ["python3", "task.py"]
