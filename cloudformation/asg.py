# system imports
import os
# 3rd party imports
from troposphere import Base64, Join
from troposphere import Parameter, Ref, Template
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.ec2 import SecurityGroupRule, SecurityGroup
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
import troposphere.autoscaling as asg

__author__ = "richardgutkowski"

def GenerateTemplate():

    t = Template()

    t.add_description("""\
    Configures auto scaling group for OpenVPN stack""")

    vpcid = t.add_parameter(Parameter(
        "VpcId",
        Default="",
        Type="String",
        Description="VpcId of your OpenVpn deployment"
    ))

    KeyName = t.add_parameter(Parameter(
        "KeyName",
        Default="",
        Type="String",
        Description="Name of an existing EC2 KeyPair to enable SSH access",
        MinLength="1",
        AllowedPattern="[\x20-\x7E]*",
        MaxLength="255",
        ConstraintDescription="can contain only ASCII characters.",
    ))

    AmiId = t.add_parameter(Parameter(
        "AmiId",
        Default="ami-90d9f5f6",
        Type="String",
        Description="The AMI id for the OpenVpn ready to deploy instance",
    ))

    PublicSubnet1 = t.add_parameter(Parameter(
        "PublicSubnet1",
        Default="",
        Type="String",
        Description="A public VPC subnet ID for the openvpn asg.",
    ))

    PublicSubnet2 = t.add_parameter(Parameter(
        "PublicSubnet2",
        Default="",
        Type="String",
        Description="A public VPC subnet ID for the openvpn asg.",
    ))

    VPCAvailabilityZone2 = t.add_parameter(Parameter(
        "VPCAvailabilityZone2",
        Default="eu-west-1a",
        MinLength="1",
        Type="String",
        Description="Second availability zone",
        MaxLength="255",
    ))

    VPCAvailabilityZone1 = t.add_parameter(Parameter(
        "VPCAvailabilityZone1",
        Default="eu-west-1b",
        MinLength="1",
        Type="String",
        Description="First availability zone",
        MaxLength="255",
    ))

    OpenVpnSecurityGroup = t.add_resource(SecurityGroup(
            'OpenVpnSecurityGroup',
            GroupDescription='OpenVpn ports with recommended settings',
            SecurityGroupIngress=[
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='443',
                    ToPort='443',
                    CidrIp='0.0.0.0/0'),
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='943',
                    ToPort='943',
                    CidrIp='0.0.0.0/0'),
                SecurityGroupRule(
                    IpProtocol='udp',
                    FromPort='1194',
                    ToPort='1194',
                    CidrIp='0.0.0.0/0'),
            ],
            VpcId=Ref(vpcid),
    ))

    LaunchConfiguration = t.add_resource(asg.LaunchConfiguration(
        "LaunchConfiguration",
        UserData=Base64(Join('', [
            "#!/bin/bash\n",

            "### Deploy app \n",
            "aws s3 cp s3://s3BucketURL/ansible /opt/ansible --recursive --region eu-west-1", "\n",
            "#ansible-playbook -i localhost /opt/ansible/site.yml -v", "\n"
        ])),
        ImageId=Ref(AmiId),
        KeyName=Ref(KeyName),
        SecurityGroups=[Ref(OpenVpnSecurityGroup)],
        InstanceType="t2.small",
        IamInstanceProfile="",
    ))

    AutoScalingGroup = t.add_resource(asg.AutoScalingGroup(
        "AutoscalingGroup",
        DesiredCapacity="1",
        LaunchConfigurationName=Ref(LaunchConfiguration),
        MinSize="1",
        MaxSize="1",
        Tags=[
            Tag("Name", "OpenVPN-AutoScalingGroup-Instance", True)
        ],
        VPCZoneIdentifier=[Ref(PublicSubnet1), Ref(PublicSubnet2)],
        AvailabilityZones=[Ref(VPCAvailabilityZone1), Ref(VPCAvailabilityZone2)],
        HealthCheckType="EC2",
        HealthCheckGracePeriod=45,
        UpdatePolicy=UpdatePolicy(
            AutoScalingReplacingUpdate=AutoScalingReplacingUpdate(
                WillReplace=True,
            ),
            AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                PauseTime='PT5M',
                MinInstancesInService="0",
                MaxBatchSize='1',
                WaitOnResourceSignals=True
            )
        )
    ))

    return t

if __name__ == '__main__':
    template = GenerateTemplate()
    template_filename = "openvpn_asg_template" + '.json'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'output')
    try:
        os.makedirs(output_dir)
    except OSError:
        pass
    path = os.path.join(output_dir, template_filename)
    with open(path, 'w') as json_file:
        json_file.write(template.to_json())
        print ('CFN Json template is saved in %s directory as %s' %(output_dir,template_filename))