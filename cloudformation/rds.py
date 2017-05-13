# system imports
import os
# 3rd party imports
from troposphere import GetAtt, Join, Output, Parameter, Ref, Template
from troposphere.ec2 import Tag
from troposphere.ec2 import SecurityGroup
from troposphere.rds import DBInstance, DBSubnetGroup

__author__ = "richardgutkowski"

def GenerateTemplate():

    t = Template()

    t.add_description("""\
        CloudFormation template which creates an RDS DBInstance for the OpenVPN stack
        """)

    vpcid = t.add_parameter(Parameter(
        "VpcId",
        Default="",
        Type="String",
        Description="VpcId of your existing Virtual Private Cloud (VPC)"
    ))

    subnet = t.add_parameter(Parameter(
        "Subnets",
        Default="subnet-,subnet-",
        Type="CommaDelimitedList",
        Description=(
            "The list of SubnetIds, for at least two Availability Zones in the "
            "region in your Virtual Private Cloud (VPC)")
    ))

    dbname = t.add_parameter(Parameter(
        "DBName",
        Default="OpenVPNDatabase",
        Description="The OpenVPN database",
        Type="String",
        MinLength="1",
        MaxLength="64",
        AllowedPattern="[a-zA-Z][a-zA-Z0-9]*",
        ConstraintDescription=("must begin with a letter and contain only"
                               " alphanumeric characters.")
    ))

    dbuser = t.add_parameter(Parameter(
        "DBUser",
        NoEcho=True,
        Description="The database admin account username",
        Type="String",
        MinLength="1",
        MaxLength="16",
        AllowedPattern="[a-zA-Z][a-zA-Z0-9]*",
        ConstraintDescription=("must begin with a letter and contain only"
                               " alphanumeric characters.")
    ))

    dbpassword = t.add_parameter(Parameter(
        "DBPassword",
        NoEcho=True,
        Description="The database admin account password",
        Type="String",
        MinLength="1",
        MaxLength="41",
        AllowedPattern="[a-zA-Z0-9]*",
        ConstraintDescription="must contain only alphanumeric characters."
    ))

    dbclass = t.add_parameter(Parameter(
        "DBClass",
        Default="db.t2.small",
        Description="Database instance class",
        Type="String",
        AllowedValues=[
            "db.t2.micro", "db.t2.small", "db.t2.medium", "db.t2.large", "db.m1.small",
            "db.m1.large", "db.m1.xlarge", "db.m2.xlarge", "db.m2.2xlarge", "db.m2.4xlarge"],
        ConstraintDescription="must select a valid database instance type.",
    ))

    dballocatedstorage = t.add_parameter(Parameter(
        "DBAllocatedStorage",
        Default="5",
        Description="The size of the database (Gb)",
        Type="Number",
        MinValue="5",
        MaxValue="1024",
        ConstraintDescription="must be between 5 and 1024Gb.",
    ))

    mydbsubnetgroup = t.add_resource(DBSubnetGroup(
        "MyDBSubnetGroup",
        DBSubnetGroupDescription="Subnets available for the RDS DB Instance",
        SubnetIds=Ref(subnet),
    ))

    myvpcsecuritygroup = t.add_resource(SecurityGroup(
        "myVPCSecurityGroup",
        GroupDescription="Security group for RDS DB Instance.",
        VpcId=Ref(vpcid)
    ))

    openvpndb = t.add_resource(DBInstance(
        "Openvpndb",
        DBName=Ref(dbname),
        AllocatedStorage=Ref(dballocatedstorage),
        DBInstanceClass=Ref(dbclass),
        Engine="MySQL",
        EngineVersion="5.6.23",
        MasterUsername=Ref(dbuser),
        MasterUserPassword=Ref(dbpassword),
        DBSubnetGroupName=Ref(mydbsubnetgroup),
        VPCSecurityGroups=[Ref(myvpcsecuritygroup)],
        Tags=[
            Tag("Name", "OpenVpn-db"),
            Tag("ApplicationStack", "OpenVPN"),
            Tag("Type", "database")
        ],
    ))

    t.add_output(Output(
        "JDBCConnectionString",
        Description="JDBC connection string for database",
        Value=Join("", [
            "jdbc:mysql://",
            GetAtt("Openvpndb", "Endpoint.Address"),
            GetAtt("Openvpndb", "Endpoint.Port"),
            "/",
            Ref(dbname)
        ])
    ))

    return t

if __name__ == '__main__':
    template = GenerateTemplate()
    template_filename = "openvpn_rds_template" + '.json'
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