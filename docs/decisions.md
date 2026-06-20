# Decision log

## Formato

```text
Decision:
Contexto:
Alternativas:
Tradeoff:
Resultado:
```

## Decisiones

### 001 - Laboratorios locales

Decision: usar Docker Compose, MinIO y LocalStack en lugar de cuentas AWS personales.

Contexto: evitar costos accidentales y reducir friccion de setup.

Tradeoff: no se practica consola AWS real en profundidad.

Resultado: los labs son reproducibles y reutilizables.

### 003 - Formato de eventos crudos

Decision: JSONL (JSON Lines) para data/raw/events.jsonl.

Contexto: los eventos se generan uno por vez. JSONL permite procesar con streaming
sin cargar todo el archivo en memoria, y es fácil de appender.

Alternativas: JSON array, CSV, Parquet.

Tradeoff: JSONL no es legible de un vistazo como un JSON array formateado.
Parquet sería más eficiente a escala, pero requiere dependencias externas.

Resultado: JSONL para raw. CSV para processed (compatibilidad analítica máxima).

### 004 - Pipeline de procesamiento

Decision: script Python (process_events.py) lee JSONL y escribe JSON filtrado.

Contexto: necesitamos filtrar un subconjunto de eventos GitHub Archive para análisis.
El script es reproducible: misma entrada, misma salida, sin efectos secundarios.

Tradeoff: un script por transformación vs una sola función general.
Elegimos un script por transformación: más legible, más fácil de testear.

Resultado: process_events.py → data/processed/push_events.json (filtra PushEvent)

### 002 - Entorno de desarrollo

Decision: GitHub Codespaces.

Contexto: el grupo no tiene instalaciones homogéneas (mix de macOS, Windows y Linux).
Codespaces ofrece el mismo entorno para todos sin configuración local.

Alternativas: Docker Desktop local, WSL2, máquina virtual.

Tradeoff: depende de conectividad y de los free-tier hours disponibles (60 hs/mes por cuenta).
Con Docker local se trabaja offline y sin límite de tiempo.

Resultado: Codespaces para las clases, Docker local como fallback documentado en el README.


@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ docker compose up -d
[+] Running 5/5
 ✔ Container cloud-foundations-redis       Running                                                               0.0s 
 ✔ Container cloud-foundations-localstack  Running                                                               0.0s 
 ✔ Container cloud-foundations-minio       Running                                                               0.0s 
 ✔ Container cloud-foundations-redpanda    Started                                                               0.5s 
 ✔ Container cloud-foundations-postgres    Started                                                               0.6s 
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam get-role --role-name app-role --query "Role.Arn"
awslocal s3 ls s3://course-data-raw

aws: [ERROR]: An error occurred (NoSuchEntity) when calling the GetRole operation: Role app-role not found

aws: [ERROR]: An error occurred (NoSuchBucket) when calling the ListObjectsV2 operation: The specified bucket does not exist
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ python scripts/iam_demo.py
=== Lab 04 — IAM demo ===

AVISO: LocalStack Community no enforcea policies (Deny no bloquea).
       Practicamos la mecánica: crear, adjuntar, asumir.

1. Bucket S3
  bucket 'course-data-raw' creado con objeto de ejemplo

2. Grupo + policy administrada
  grupo 'bigdata-read' creado
  policy 'S3ReadOnlyLab' creada: arn:aws:iam::000000000000:policy/S3ReadOnlyLab
  policy adjuntada al grupo 'bigdata-read'

3. Usuario → grupo
  usuario 'lab-user' creado
  usuario 'lab-user' agregado al grupo 'bigdata-read'
  access key creada: LKIAQAAAAAAAGHC2FOAJ (larga duración — evitar en prod)

4. Rol con trust policy (EC2) + inline policy mínima
  rol 'app-role' creado
  inline policy 'InlineS3Read' adjuntada al rol 'app-role'

5. AssumeRole vía STS → credenciales temporales

  asumiendo rol: arn:aws:iam::000000000000:role/app-role
  AccessKeyId:  LSIAQAAAAAAAEY4JR7E2
  Expiration:   2026-06-20 21:00:02.707000+00:00  ← credencial temporal
  objetos en 'course-data-raw' con credenciales temporales:
    - sample/hello.txt (17 bytes)

=== Resumen de recursos creados ===
  Bucket:  course-data-raw
  Grupo:   bigdata-read
  Policy:  arn:aws:iam::000000000000:policy/S3ReadOnlyLab
  Usuario: lab-user
  Rol:     arn:aws:iam::000000000000:role/app-role

Listo. Revisá los JSON en iam/ para entender cada documento.
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 create-key-pair --key-name lab05-key --query "KeyFingerprint"
"70:8c:8b:9c:94:d0:31:d0:bf:fa:5b:dd:59:ca:64:f0"
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ SG_ID=$(awslocal ec2 create-security-group \
  --group-name web-sg \
  --description "Lab 05 — HTTP público, SSH restringido" \
  --query "GroupId" --output text)

echo "SG: $SG_ID"
SG: sg-cc80bf8898d42e020
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 80 --cidr 0.0.0.0/0
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-a680acf48a04bcae5",
            "GroupId": "sg-cc80bf8898d42e020",
            "GroupOwnerId": "000000000000",
            "IsEgress": false,
            "IpProtocol": "tcp",
            "FromPort": 80,
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 22 --cidr 0.0.0.0/0
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-2bae219a6d5b60846",
            "GroupId": "sg-cc80bf8898d42e020",
            "GroupOwnerId": "000000000000",
            "IsEgress": false,
            "IpProtocol": "tcp",
            "FromPort": 22,
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 describe-security-groups --group-ids $SG_ID
{
    "SecurityGroups": [
        {
            "GroupId": "sg-cc80bf8898d42e020",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam create-instance-profile --instance-profile-name app-instance-profile

awslocal iam add-role-to-instance-profile \
  --instance-profile-name app-instance-profile \
  --role-name app-role

awslocal iam get-instance-profile --instance-profile-name app-instance-profile
{
    "InstanceProfile": {
        "Path": "/",
        "InstanceProfileName": "app-instance-profile",
        "InstanceProfileId": "qqsb86zuqrj77w6soy99",
        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
        "CreateDate": "2026-06-20T20:46:33.683000+00:00",
        "Roles": [],
        "Tags": []
    }
{
    "InstanceProfile": {
        "Path": "/",
        "InstanceProfileName": "app-instance-profile",
        "InstanceProfileId": "qqsb86zuqrj77w6soy99",
        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
        "CreateDate": "2026-06-20T20:46:33.683000+00:00",
        "Roles": [
            {
                "Path": "/",
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam get-instance-profile --instance-profile-name app-instance-profile
{
    "InstanceProfile": {
        "Path": "/",
        "InstanceProfileName": "app-instance-profile",
        "InstanceProfileId": "qqsb86zuqrj77w6soy99",
        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
        "CreateDate": "2026-06-20T20:46:33.683000+00:00",
        "Roles": [
            {
                "Path": "/",
                "RoleName": "app-role",
                "RoleId": "AROAQAAAAAAAJT342QW4Y",
                "Arn": "arn:aws:iam::000000000000:role/app-role",
                "CreateDate": "2026-06-20T20:45:02.575000+00:00",
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ec2.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
            }
        ],
        "Tags": []
    }
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ INSTANCE_ID=$(awslocal ec2 run-instances \
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ INSTANCE_ID=$(awslocal ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.micro \
  --count 1 \lab05-key \
  --key-name lab05-key \SG_ID \
  --security-group-ids $SG_ID \ata.sh \
  --user-data file://ec2/user_data.sh \nce-profile \
  --iam-instance-profile Name=app-instance-profile \{Key=Name,Value=lab05-web},{Key=Lab,Value=05}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lab05-web},{Key=Lab,Value=05}]' \
  --query "Instances[0].InstanceId" --output text)
echo "Instance: $INSTANCE_ID"
echo "Instance: $INSTANCE_ID"
Instance: i-03d5b0679a5177c64
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 describe-instances --instance-ids $INSTANCE_ID
{
    "Reservations": [
        {
            "ReservationId": "r-3253bdb8",
            "OwnerId": "000000000000",
            "Groups": [],
            "Instances": [
                {
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2026-06-20T20:47:16+00:00",
                                "DeleteOnTermination": true,
                                "Status": "in-use",
                                "VolumeId": "vol-6db0b32f"
                            }
                        }
                    ],
                    "ClientToken": "ABCDE0000000000003",
                    "EbsOptimized": false,
                    "Hypervisor": "xen",
                    "IamInstanceProfile": {
                        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
                        "Id": "iip-assoc-1ee78afe"
                    },
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "000000000000",
                                "PublicIp": "54.214.56.219"
                            },
                            "Attachment": {
                                "AttachTime": "2015-01-01T00:00:00+00:00",
                                "AttachmentId": "eni-attach-e4ea41a4",
                                "DeleteOnTermination": true,
                                "DeviceIndex": 0,
                                "Status": "attached"
                            },
                            "Description": "Primary network interface",
                            "Groups": [
                                {
                                    "GroupId": "sg-cc80bf8898d42e020",
                                    "GroupName": "web-sg"
                                }
                            ],
                            "MacAddress": "1b:2b:3c:4d:5e:6f",
                            "NetworkInterfaceId": "eni-79e674df",
                            "OwnerId": "000000000000",
                            "PrivateIpAddress": "10.25.48.134",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "000000000000",
                                        "PublicIp": "54.214.56.219"
                                    },
                                    "Primary": true,
                                    "PrivateIpAddress": "10.25.48.134"
                                }
                            ],
                            "SourceDestCheck": true,
                            "Status": "in-use",
                            "SubnetId": "subnet-bd861af5",
                            "VpcId": "vpc-e30f7673"
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupId": "sg-cc80bf8898d42e020",
                            "GroupName": "web-sg"
                        }
                    ],
                    "SourceDestCheck": true,
                    "StateReason": {
                        "Code": "",
                        "Message": ""
                    },
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "lab05-web"
                        },
                        {
                            "Key": "Lab",
                            "Value": "05"
                        }
                    ],
                    "VirtualizationType": "paravirtual",
                    "InstanceId": "i-03d5b0679a5177c64",
                    "ImageId": "ami-0c02fb55956c7d316",
                    "State": {
                        "Code": 16,
                        "Name": "running"
                    },
                    "PrivateDnsName": "ip-10-25-48-134.ec2.internal",
                    "PublicDnsName": "ec2-54-214-56-219.compute-1.amazonaws.com",
                    "StateTransitionReason": "",
                    "KeyName": "lab05-key",
                    "AmiLaunchIndex": 0,
                    "InstanceType": "t3.micro",
                    "LaunchTime": "2026-06-20T20:47:16+00:00",
                    "Placement": {
                        "GroupName": "",
                        "Tenancy": "default",
                        "AvailabilityZone": "us-east-1a"
                    },
                    "KernelId": "None",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "SubnetId": "subnet-bd861af5",
                    "VpcId": "vpc-e30f7673",
                    "PrivateIpAddress": "10.25.48.134",
                    "PublicIpAddress": "54.214.56.219"
                }
            ]
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 describe-instance-attribute \
  --instance-id $INSTANCE_ID \
  --attribute userData \
  --query "UserData.Value" --output text | base64 --decode | head -10
#!/bin/bash
# Lab 05 — user-data: bootstrap de una instancia que sirve contenido bajado de S3.
#
# Cierre del círculo IAM → EC2 → S3:
#   - La instancia tiene asociado el instance profile "app-instance-profile"
#   - Ese profile expone el rol "app-role" (creado en lab-04) con s3:GetObject
#   - aws s3 cp usa esas credenciales temporales vía IMDSv2 — sin claves en disco
#
# En AWS real este script corre la primera vez que arranca la instancia.
# En LocalStack Community se almacena pero NO se ejecuta (EC2 es mock).
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ python scripts/ec2_demo.py
=== Lab 05 — EC2 demo: IAM → EC2 → S3 ===

AVISO: LocalStack Community mock-ea EC2.
       El flujo CLI/API es real; la VM no arranca y el user-data no se ejecuta.

1. Key pair
  key pair 'lab05-key' ya existe

2. Security group + reglas de ingress
  security group 'web-sg' ya existe: sg-cc80bf8898d42e020
  ingress permitido: tcp/80
  ingress permitido: tcp/22

3. Instance profile (wrapper del rol app-role del lab-04)
  instance profile 'app-instance-profile' ya existe
  rol 'app-role' ya estaba adjuntado
   profile ARN: arn:aws:iam::000000000000:instance-profile/app-instance-profile

4. run-instances con user-data + profile
  instancia lanzada: i-9f350f3e94f42c74f (t3.micro, AMI ami-0c02fb55956c7d316)

5. describe-instances — ver lo que quedó aprovisionado
  estado: running
  AMI:    ami-0c02fb55956c7d316
  type:   t3.micro
  SG:     ['web-sg']
  profile: arn:aws:iam::000000000000:instance-profile/app-instance-profile

6. describe-instance-attribute — user-data almacenado
  user-data cargado (1398 chars). Primera línea: '#!/bin/bash'

=== Resumen ===
  Key pair:         lab05-key
  Security group:   web-sg (sg-cc80bf8898d42e020)
  Instance profile: app-instance-profile
  Instancia:        i-9f350f3e94f42c74f

Para terminar la instancia (no olvidar — cattle, not pets):
  awslocal ec2 terminate-instances --instance-ids i-9f350f3e94f42c74f
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 stop-instances --instance-ids $INSTANCE_ID
{
    "StoppingInstances": [
        {
            "InstanceId": "i-03d5b0679a5177c64",
            "CurrentState": {
                "Code": 64,
                "Name": "stopping"
            },
            "PreviousState": {
                "Code": 16,
                "Name": "running"
            }
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 start-instances --instance-ids $INSTANCE_ID
{
    "StartingInstances": [
        {
            "InstanceId": "i-03d5b0679a5177c64",
            "CurrentState": {
                "Code": 0,
                "Name": "pending"
            },
            "PreviousState": {
                "Code": 80,
                "Name": "stopped"
            }
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 terminate-instances --instance-ids $INSTANCE_ID
{
    "TerminatingInstances": [
        {
            "InstanceId": "i-03d5b0679a5177c64",
            "CurrentState": {
                "Code": 32,
                "Name": "shutting-down"
            },
            "PreviousState": {
                "Code": 16,
                "Name": "running"
            }
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 delete-security-group --group-id $SG_ID
awslocal ec2 delete-key-pair --key-name lab05-key
{
    "Return": true
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal ec2 delete-key-pair --key-name lab05-key
{
    "Return": true
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam remove-role-from-instance-profile \
> q

aws: [ERROR]: An error occurred (ParamValidation): the following arguments are required: --instance-profile-name, --role-name

usage: aws [options] <command> <subcommand> [<subcommand> ...] [parameters]
To see help text, you can run:

  aws help
  aws <command> help
  aws <command> <subcommand> help

@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam remove-role-from-instance-profile 

aws: [ERROR]: An error occurred (ParamValidation): the following arguments are required: --instance-profile-name, --role-name

usage: aws [options] <command> <subcommand> [<subcommand> ...] [parameters]
To see help text, you can run:

  aws help
  aws <command> help
  aws <command> <subcommand> help

@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam remove-role-from-instance-profile \
  --instance-profile-name app-instance-profile --role-name app-role
awslocal iam delete-instance-profile --instance-profile-name app-instance-profile
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $  `awslocal --version`
bash: aws-cli/2.35.8: No such file or directory
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ python ^C
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ python awslocal --version
python: can't open file '/workspaces/cloud-foundations-lab/awslocal': [Errno 2] No such file or directory
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal iam get-role --role-name app-role --query "Role.Arn"
"arn:aws:iam::000000000000:role/app-role"
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 ls 
2026-06-20 20:45:02 course-data-raw
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 mb s3://course-data-lake
make_bucket: course-data-lake
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api put-public-access-block \
  --bucket course-data-lake \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api put-bucket-encryption \
  --bucket course-data-lake \
  --server-side-encryption-configuration '{
    "Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]
  }'
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api get-public-access-block --bucket course-data-lake
awslocal s3api get-bucket-encryption --bucket course-data-lake
{
    "PublicAccessBlockConfiguration": {
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }
}
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api put-bucket-versioning \
  --bucket course-data-lake \
  --versioning-configuration Status=Enabled

awslocal s3api get-bucket-versioning --bucket course-data-lake
{
    "Status": "Enabled"
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 sync data/raw/olist/ s3://course-data-lake/raw/olist/
upload: data/raw/olist/category_translations.csv to s3://course-data-lake/raw/olist/category_translations.csv
upload: data/raw/olist/order_items.csv to s3://course-data-lake/raw/olist/order_items.csv
upload: data/raw/olist/customers.csv to s3://course-data-lake/raw/olist/customers.csv
upload: data/raw/olist/order_reviews.csv to s3://course-data-lake/raw/olist/order_reviews.csv
upload: data/raw/olist/orders.csv to s3://course-data-lake/raw/olist/orders.csv
upload: data/raw/olist/sellers.csv to s3://course-data-lake/raw/olist/sellers.csv
upload: data/raw/olist/order_payments.csv to s3://course-data-lake/raw/olist/order_payments.csv
upload: data/raw/olist/products.csv to s3://course-data-lake/raw/olist/products.csv
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 sync data/raw/events/ s3://course-data-lake/raw/events/
upload: data/raw/events/github_events.jsonl to s3://course-data-lake/raw/events/github_events.jsonl
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 sync data/processed/ s3://course-data-lake/processed/
upload: data/processed/.gitkeep to s3://course-data-lake/processed/.gitkeep
upload: data/processed/push_events.json to s3://course-data-lake/processed/push_events.json
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 ls s3://course-data-lake --recursive | head
2026-06-20 20:58:45          1 processed/.gitkeep
2026-06-20 20:58:45     395385 processed/push_events.json
2026-06-20 20:58:31     418698 raw/events/github_events.jsonl
2026-06-20 20:58:20       2613 raw/olist/category_translations.csv
2026-06-20 20:58:20     262528 raw/olist/customers.csv
2026-06-20 20:58:20     456173 raw/olist/order_items.csv
2026-06-20 20:58:20     173990 raw/olist/order_payments.csv
2026-06-20 20:58:20     425033 raw/olist/order_reviews.csv
2026-06-20 20:58:20     528854 raw/olist/orders.csv
2026-06-20 20:58:20     152276 raw/olist/products.csv
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 cp s3://course-data-lake/raw/olist/orders.csv /tmp/orders.csv
download: s3://course-data-lake/raw/olist/orders.csv to ../../tmp/orders.csv
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ echo "NEW_ORDER_2026_FICTICIO,99999,delivered,2026-06-18,2026-06-19,2026-06-25,," >> /tmp/orders.csv
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 cp /tmp/orders.csv s3://course-data-lake/raw/olist/orders.csv
upload: ../../tmp/orders.csv to s3://course-data-lake/raw/olist/orders.csv
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api list-object-versions \
  --bucket course-data-lake \
  --prefix raw/olist/orders.csv \
  --query "Versions[].{Id:VersionId,Size:Size,Latest:IsLatest}"
[
    {
        "Id": "BRBq0_HpLfftZ07v8eB.paV8HNv.7Xk6",
        "Size": 528929,
        "Latest": true
    },
    {
        "Id": "HHEhIdv0NztVDDo_C1i9_MMhc.Z9_I_t",
        "Size": 528854,
        "Latest": false
    }
]
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api put-bucket-policy \
  --bucket course-data-lake \
  --policy file://s3/bucket_policy.json
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api get-bucket-policy --bucket course-data-lake --query Policy --output text | python3 -m json.tool
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowInstanceRoleReadObjects",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::000000000000:role/app-role"
            },
            "Action": "s3:GetObject",
            "Resource": [
                "arn:aws:s3:::course-data-lake/raw/*",
                "arn:aws:s3:::course-data-lake/processed/*"
            ]
        },
        {
            "Sid": "AllowInstanceRoleListBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::000000000000:role/app-role"
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::course-data-lake",
            "Condition": {
                "StringLike": {
                    "s3:prefix": [
                        "raw/*",
                        "processed/*"
                    ]
                }
            }
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ # Asumir el rol (en AWS real esto lo hace la EC2 automáticamente vía IMDSv2)                                          # Asumir el rol (en AWS real esto lo hace la EC2 automáticamente vía IMDSv2)assume-role \
CREDS=$(awslocal sts assume-role \0000:role/app-role \
  --role-arn arn:aws:iam::000000000000:role/app-role \
  --role-session-name lab06-download \
  --duration-seconds 900 \tput json)
  --query Credentials --output json)
export AWS_ACCESS_KEY_ID=$(echo $CREDS | python3 -c "import json,sys;print(json.load(sys.stdin)['AccessKeyId'])")
export AWS_ACCESS_KEY_ID=$(echo $CREDS | python3 -c "import json,sys;print(json.load(sys.stdin)['AccessKeyId'])")Key']
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | python3 -c "import json,sys;print(json.load(sys.stdin)['SecretAccessKey'])")ort AWS_SESSION_TOKEN=$(echo $CREDS | python3 -c "import json,sys;print(json.load(sys.stdin)['SessionToken'])")
export AWS_SESSION_TOKEN=$(echo $CREDS | python3 -c "import json,sys;print(json.load(sys.stdin)['SessionToken'])")
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 cp s3://course-data-lake/raw/olist/customers.csv /tmp/customers.csv
head -3 /tmp/customers.csv
download: s3://course-data-lake/raw/olist/customers.csv to ../../tmp/customers.csv
customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state
18955e83d337fd6b2def6b18a428ac77,290c77bc529b7ac935b93aa66c333dc3,09790,sao bernardo do campo,SP
fd826e7cf63160e536e0908c76c3f441,addec96d2e059c80c30fe6871d30d177,04534,sao paulo,SP
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ unset AWS_SESSION_TOKEN
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3 presign s3://course-data-lake/processed/push_events.json --expires-in 300
http://localhost:4566/course-data-lake/processed/push_events.json?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=test%2F20260620%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260620T210305Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&X-Amz-Signature=13e39ec9a965c6d6422bfbaa8d602cf74b36e79fbb48aeac9a18c88715e73278
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ python scripts/s3_demo.py
=== Lab 06 — S3 data lake + cierre IAM → EC2 → S3 ===

1. Bucket
  bucket 'course-data-lake' creado

2. Hardening por defecto (BPA + encryption)
  Block Public Access: ON (4 flags)
  Encryption: SSE-S3 (AES256) por defecto

3. Versioning
  Versioning: Enabled

4. Upload del dataset (Olist + GitHub Archive + processed)
  1 objetos nuevos (0.5 MB)
    - raw/olist/orders.csv (528,854 bytes)
  9 objetos ya estaban en S3 (skip)

5. Demo versioning (sobrescribir orders.csv)
  sobrescrito: raw/olist/orders.csv (+1 fila ficticia)
  versiones de 'raw/olist/orders.csv': 4
    - VersionId=Y2ix.rZhjFjROT26... Size=528,930 ← actual
    - VersionId=8.5svPgWcEZjz59r... Size=528,854
    - VersionId=BRBq0_HpLfftZ07v... Size=528,929

6. Bucket policy: solo app-role puede leer
  bucket policy aplicada: GetObject + ListBucket para app-role sobre raw/* y processed/*

7. AssumeRole + GetObject — cierre del círculo
  asumiendo rol app-role...
  creds temporales obtenidas (expiran: 2026-06-20 21:18:22.386000+00:00)
  GetObject como app-role: 'raw/olist/customers.csv' OK (262,528 bytes)

8. Presigned URL — acceso temporario sin asumir rol
  presigned URL para 'processed/push_events.json' (válida 5 min):
    http://localhost:4566/course-data-lake/processed/push_events.json?AWSAccessKeyId=test&Signature=eBC7...

=== Resumen final ===
  objetos:   11
  versiones: 14 (incluye sobreescritas)
  tamaño:    2.7 MB

Bucket en S3: s3://course-data-lake/
Listar todo: awslocal s3 ls s3://course-data-lake --recursive
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-06-ejemplo) $ awslocal s3api list-object-versions \
  --bucket course-data-lake \
  --prefix raw/olist/orders.csv \
  --query "Versions[?!IsLatest].{Key:Key,VersionId:VersionId}"

# Borrar una versión específica (reemplazar VERSION_ID)
awslocal s3api delete-object \
  --bucket course-data-lake \
  --key raw/olist/orders.csv \
  --version-id <VERSION_ID>
bash: !IsLatest].{Key: event not found
{
    "Versions": [
        {
            "ETag": "\"2c555a6d31c3090e3c9e38a429cf5c33\"",
            "ChecksumAlgorithm": [
                "CRC32"
            ],
            "Size": 528930,
            "StorageClass": "STANDARD",
            "Key": "raw/olist/orders.csv",
            "VersionId": "Y2ix.rZhjFjROT26SvCS.X.OludCwvPF",
            "IsLatest": true,
            "LastModified": "2026-06-20T21:03:22+00:00",
            "Owner": {
                "DisplayName": "webfile",
                "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
            }
        },
        {
            "ETag": "\"f65e1a398f6fa141350e7b27f529f5ca\"",
            "ChecksumAlgorithm": [
                "CRC32"
            ],
            "Size": 528854,
            "StorageClass": "STANDARD",
            "Key": "raw/olist/orders.csv",
            "VersionId": "8.5svPgWcEZjz59ri7fFlB7Hqh34fQP6",
            "IsLatest": false,
            "LastModified": "2026-06-20T21:03:22+00:00",
            "Owner": {
                "DisplayName": "webfile",
                "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
            }
        },
        {
            "ETag": "\"1a25de80364a3ecd3707ffbf359329d7\"",
            "Size": 528929,
            "StorageClass": "STANDARD",
            "Key": "raw/olist/orders.csv",
            "VersionId": "BRBq0_HpLfftZ07v8eB.paV8HNv.7Xk6",
            "IsLatest": false,
            "LastModified": "2026-06-20T20:59:56+00:00",
            "Owner": {
                "DisplayName": "webfile",
                "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
            }
        },
        {
            "ETag": "\"f65e1a398f6fa141350e7b27f529f5ca\"",
            "Size": 528854,
            "StorageClass": "STANDARD",
            "Key": "raw/olist/orders.csv",
            "VersionId": "HHEhIdv0NztVDDo_C1i9_MMhc.Z9_I_t",
            "IsLatest": false,
            "LastModified": "2026-06-20T20:58:20+00:00",
            "Owner": {
                "DisplayName": "webfile",
                "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
            }
        }
    ],
    "RequestCharged": null,
    "Prefix": "raw/olist/orders.csv"
}
bash: syntax error near unexpected token `newline'