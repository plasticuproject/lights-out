FROM python:3.11-alpine

# permissions and nonroot user stuff
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
WORKDIR /home/app
USER nonroot

# copy python code to the container
COPY --chown=nonroot:nonroot lights_out.py .

CMD ["python3", "lights_out.py"]
