This repository is a POC on how to send notification using Server Sent Events and Pub/Sub.

[Documentation](https://jinayshah86.notion.site/Notification-services-06d24c1d339e4fb09103250f56f6bb66)

## Local setup
1. Create a virtual environment
    ```
    conda create --name sse-notification python=3.9
    ```
2. Activate virtual environment
    ```
    conda activate sse-notification
    ```
3. Install python packages
    ```
    pip install -r requirements
    ```

### Start the server
```
docker-compose up -d backend
```

### Stop the server
```
docker-compose down
```

### Publish messages
```
curl -X 'POST' \
  'http://localhost:8000/event/temp' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"foo": "bar"}'
```

### Subscribe to the event stream
Open the browser and paste the following code to the console
```
const eventSource = new EventSource("http://localhost:8000/stream/temp");
eventSource.addEventListener("update", function(event) {
    // Logic to handle status updates
    console.log(event)
});
eventSource.addEventListener("end", function(event) {
    console.log('Handling end....')
    eventSource.close();
});
```
