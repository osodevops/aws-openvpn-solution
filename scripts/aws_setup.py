"""
Setup script to get the s3 buckets in place for deployments
"""

import boto3

aws_credentials = raw_input("Please provide your aws profile: ")

session = boto3.Session(profile_name='%s' %(aws_credentials))

s3 = boto3.resource('s3')

s3_bucket = raw_input("Please provide a bucket name: ")

print s3.Bucket('%s' % (s3_bucket)) in s3.buckets.all()

def create_s3_bucket(name):
    if s3.Bucket('%s' %(name)) in s3.buckets.all() != True:
        s3.create_bucket(Bucket='%s' %(name), CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-1'})
        print ("Bucket %s has been created" %(name))
    else:
        s3.Bucket('%s' % (name)) in s3.buckets.all()
        print ("No such bucket or %s is already in use" %(name))

create_s3_bucket('%s' %(s3_bucket))

