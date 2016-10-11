def upload_to_s3(self, source_path, bucket_name):
    r"""
    Given a file, upload it to S3.
    Credentials should be stored in environment variables or ~/.aws/credentials (%USERPROFILE%\.aws\credentials on Windows).
    Returns True on success, false on failure.
    """
    try:
        self.s3_client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError:
        # This is really stupid S3 quirk. Technically, us-east-1 one has no S3,
        # it's actually "US Standard", or something.
        # More here: https://github.com/boto/boto3/issues/125
        if self.aws_region == 'us-east-1':
            self.s3_client.create_bucket(
                Bucket=bucket_name,
            )
        else:
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.aws_region},
            )

    if not os.path.isfile(source_path) or os.stat(source_path).st_size == 0:
        print("Problem with source file {}".format(source_path))
        return False

    dest_path = os.path.split(source_path)[1]
    try:
        source_size = os.stat(source_path).st_size
        print("Uploading {0} ({1})...".format(dest_path, self.human_size(source_size)))
        progress = tqdm(total=float(os.path.getsize(source_path)), unit_scale=True, unit='B')

        # Attempt to upload to S3 using the S3 meta client with the progress bar.
        # If we're unable to do that, try one more time using a session client,
        # which cannot use the progress bar.
        # Related: https://github.com/boto/boto3/issues/611
        try:
            self.s3_client.upload_file(
                source_path, bucket_name, dest_path,
                Callback=progress.update
            )
        except Exception as e:  # pragma: no cover
            self.s3_client.upload_file(source_path, bucket_name, dest_path)

        progress.close()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        raise
    except Exception as e:  # pragma: no cover
        print(e)
        return False
    return True

def remove_from_s3(self, file_name, bucket_name):
    """
    Given a file name and a bucket, remove it from S3.
    There's no reason to keep the file hosted on S3 once its been made into a Lambda function, so we can delete it from S3.
    Returns True on success, False on failure.
    """
    try:
        self.s3_client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:  # pragma: no cover
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            return False

    try:
        self.s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        return True
    except botocore.exceptions.ClientError:  # pragma: no cover
        return False
