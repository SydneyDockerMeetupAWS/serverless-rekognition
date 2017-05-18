# NoOps presentations
The source code for NoOps presentation in ASW SYD12.

## Description
### Dev environment
![Env](images/env.png)

### Application architecture
![App](images/arch.png)

## Prerequisites
### Rekognition collection
Since [AWS Rekognition](https://aws.amazon.com/rekognition/) is not supported by [AWS CloudFormation](https://aws.amazon.com/cloudformation/) yet the collection should be created manually and passed to the template as a parameter:
```bash
aws rekognition create-collection --collection-id "noops-poc" --region us-west-2
```

### S3 bucket
You need s3 bucket for temporary artifacts produced by `aws cloudformation package` command
```bash
aws s3api create-bucket --bucket noops-wip-pdx --region us-west-2
```

## How to deploy
* Get the code:
```bash
git clone ssh://git.amazon.com/pkg/SYD-Deployment-NoOps
```

* Create lambda packages
```bash
aws cloudformation package --template-file template.yml  --s3-bucket noops-wip-pdx  --output-template-file out.yml
```

* Deploy
```bash
aws cloudformation deploy --template-file out.yml --stack-name noopsPOC --capabilities CAPABILITY_IAM --region us-west-2
```


## How to use
### Add pictures to the collection
Prepare pictures and run using aws cli:
```bash
aws s3 cp ../pic/jolie3.jpg s3://<imagesbucket>/users/ --metadata Name=Angelina,Surname=Jolie,id=whoknows@example.com
```
* where <imagesbucket> is the name of the bucket created by the CFN deploy above.
* you can add as many pictures with the same id as you want

### Search using image
* Upload image on s3 (use the same bucket but the different prefix):
```bash
aws s3 cp ../pic/jolie4.jpg s3://<imagesbucket>/test/
```
* invoke the Search Lambda function
```bash
 aws --region us-west-2 lambda invoke --function-name <noopsPOC-Search> --invocation-type RequestResponse --payload "{ \"bucket\": \"<imagesbucket>\", \"key\": \"test/jolie4.jpg\" }" test.txt
```
