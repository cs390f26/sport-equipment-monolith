# Deploy on EC2

This document explains how to run the monolithic equipment app on an EC2 instance.

## Deploy Process

The script `deploy/userdata.sh` handles all the steps outlined in [Development](docs/deploy.md), and we can tell EC2 to run these commands at launch by putting the contents of this script in the [Cloud-init](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html#userdata-linux) which is under the userdata section of the EC2 launch wizard.

In the Launch dialog:

- Name the instance "Equipment app"
- Use the default `t3.micro` instance type
- Select your `vockey` for authentication
- Ensure that HTTP and SSH are enabled in the security group
- Open the "Advanced" tab, and scroll to the bottom.
- Paste the contents of `deploy/userdata.sh` into **User data**

When you launch the instance, AWS will boot the instance, and then run the userdata script. This will take a minute or two, but once it completes MySQL and Gunicorn will be running (i.e. the app will be deployed).

## Debugging

The Cloud-init process writes out output of the userdata script to `/var/log/cloud-init-output.log`. If the app does not start, SSH to the instance and look at this file to understand what failed.
