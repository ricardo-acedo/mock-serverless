# mock-serverless

Mock server deployed with python and serverless framework. It is integrated with AWS DynamoDB and S3 buckets.
The design of the mock server is to store customised mocks json response stored in the S3, we can call this templates. The mock can be customised with parameters stored in the json between two curly brackets (as example {{key1}}.
Moreover, we store the templates metada (as s3 location, name, URL path, etc) and user info in the dynamoDB.

You can check a starting python serverless tutorial from serverless here => https://serverless.com/blog/flask-python-rest-api-serverless-lambda-dynamodb/

## Requirements

To use this project, you need to have install serverless and a AWS account in your computer => [Install servereless](https://serverless.com/framework/docs/providers/aws/guide/quick-start/)

Install all npm dependencies

```bash
npm ci
```

Then, we are goint to create a virtualenv for python3 and all its dependencias, if you don't have virtualenv, install it with npm.

```bash
virtualenv venv --python=python3

source venv/bin/activate
```

Once we are in our virtual environment, we can install all the python modules requiered with pip install

```bash
pip install -r requirements.txt
```

## Local development

Now we are able to run our project locally, but we need some extra configuration for it. 
As we are using dynamoDB and S3, we need to mock this AWS services to run in our local development enviroment. To do it, we will use serverless framework (Recall to run this from your venv)

### DynamoDB Local

The following commands will install and start dynamodb in our local. We only need to install the first time, after that, each time we run dynamodb it will create all the tables needed for the project. You can access the shell for dynamodb in http://localhost:8000/shell

```bash
sls dynamodb install
sls dynamodb start
```

### S3 Local

Same as with DynamoDB, we need to start S3. Create a /tmp folder in your machine if it doesn't exist. Once is started, you can access it in the /tmp/mock-server-templates folder of your machine.

```bash
sls s3 start
```

### Run the server

We can run the server locally with wsgi. And our serverless is running locally!

```bash
sls wsgi serve
```


