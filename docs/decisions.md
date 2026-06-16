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
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ docker compose up -d
[+] Running 5/5
 ✔ Container cloud-foundations-localstack  Running                                                         0.0s 
 ✔ Container cloud-foundations-redpanda    Running                                                         0.0s 
 ✔ Container cloud-foundations-minio       Running                                                         0.0s 
 ✔ Container cloud-foundations-postgres    Running                                                         0.0s 
 ✔ Container cloud-foundations-redis       Running                                                         0.0s 
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal iam get-role --role-name app-role --query "Role.Arn"
awslocal s3 ls s3://course-data-raw

aws: [ERROR]: An error occurred (NoSuchEntity) when calling the GetRole operation: Role app-role not found

aws: [ERROR]: An error occurred (NoSuchBucket) when calling the ListObjectsV2 operation: The specified bucket does not exist
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ python scripts/iam_demo.py
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
  access key creada: LKIAQAAAAAAAD5E5VDAW (larga duración — evitar en prod)

4. Rol con trust policy (EC2) + inline policy mínima
  rol 'app-role' creado
  inline policy 'InlineS3Read' adjuntada al rol 'app-role'

5. AssumeRole vía STS → credenciales temporales

  asumiendo rol: arn:aws:iam::000000000000:role/app-role
  AccessKeyId:  LSIAQAAAAAAAGYH2ZR2H
  Expiration:   2026-06-16 23:21:15.577000+00:00  ← credencial temporal
  objetos en 'course-data-raw' con credenciales temporales:
    - sample/hello.txt (17 bytes)

=== Resumen de recursos creados ===
  Bucket:  course-data-raw
  Grupo:   bigdata-read
  Policy:  arn:aws:iam::000000000000:policy/S3ReadOnlyLab
  Usuario: lab-user
  Rol:     arn:aws:iam::000000000000:role/app-role

Listo. Revisá los JSON en iam/ para entender cada documento.
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 create-key-pair --key-name lab05-key --query "KeyFingerprint"
"8f:a3:cd:ce:85:e1:02:ec:e0:7c:08:e0:91:ff:65:a7"
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ SG_ID=$(awslocal ec2 create-security-group \
  --group-name web-sg \
  --description "Lab 05 — HTTP público, SSH restringido" \
  --query "GroupId" --output text)

echo "SG: $SG_ID"
SG: sg-0b9843e7a3d8d0519
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 80 --cidr 0.0.0.0/0
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-3e5c1940c78c0647d",
            "GroupId": "sg-0b9843e7a3d8d0519",
            "GroupOwnerId": "000000000000",
            "IsEgress": false,
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 22 --cidr 0.0.0.0/0
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-77b15b67fcb93d563",
            "GroupId": "sg-0b9843e7a3d8d0519",
            "GroupOwnerId": "000000000000",
            "IsEgress": false,
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 describe-security-groups --group-ids $SG_ID
{
    "SecurityGroups": [
        {
            "GroupId": "sg-0b9843e7a3d8d0519",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal iam create-instance-profile --instance-profile-name app-instance-profile

awslocal iam add-role-to-instance-profile \
  --instance-profile-name app-instance-profile \
  --role-name app-role

awslocal iam get-instance-profile --instance-profile-name app-instance-profile
{
    "InstanceProfile": {
        "Path": "/",
        "InstanceProfileName": "app-instance-profile",
        "InstanceProfileId": "vzfa0qsxo5s9ayxde4ba",
        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
        "CreateDate": "2026-06-16T23:09:39.643000+00:00",
        "Roles": [],
        "Tags": []
    }
}
{
    "InstanceProfile": {
        "Path": "/",
        "InstanceProfileName": "app-instance-profile",
        "InstanceProfileId": "vzfa0qsxo5s9ayxde4ba",
        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
        "CreateDate": "2026-06-16T23:09:39.643000+00:00",
        "Roles": [
            {
                "Path": "/",
                "RoleName": "app-role",
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ INSTANCE_ID=$(awslocal ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.micro \
  --count 1 \
  --key-name lab05-key \
  --security-group-ids $SG_ID \
  --user-data file://ec2/user_data.sh \
  --iam-instance-profile Name=app-instance-profile \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lab05-web},{Key=Lab,Value=05}]' \
  --query "Instances[0].InstanceId" --output text)

echo "Instance: $INSTANCE_ID"
Instance: i-8a33d347e70f4d92f
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 describe-instances --instance-ids $INSTANCE_ID
{
    "Reservations": [
        {
            "ReservationId": "r-e8e48596",
            "OwnerId": "000000000000",
            "Groups": [],
            "Instances": [
                {
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2026-06-16T23:10:44+00:00",
                                "DeleteOnTermination": true,
                                "Status": "in-use",
                                "VolumeId": "vol-63301891"
                            }
                        }
                    ],
                    "ClientToken": "ABCDE0000000000003",
                    "EbsOptimized": false,
                    "Hypervisor": "xen",
                    "IamInstanceProfile": {
                        "Arn": "arn:aws:iam::000000000000:instance-profile/app-instance-profile",
                        "Id": "iip-assoc-650f3f5b"
                    },
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "000000000000",
                                "PublicIp": "54.214.63.236"
                            },
                            "Attachment": {
                                "AttachTime": "2015-01-01T00:00:00+00:00",
                                "AttachmentId": "eni-attach-3af94471",
                                "DeleteOnTermination": true,
                                "DeviceIndex": 0,
                                "Status": "attached"
                            },
                            "Description": "Primary network interface",
                            "Groups": [
                                {
                                    "GroupId": "sg-0b9843e7a3d8d0519",
                                    "GroupName": "web-sg"
                                }
                            ],
                            "MacAddress": "1b:2b:3c:4d:5e:6f",
                            "NetworkInterfaceId": "eni-398f6914",
                            "OwnerId": "000000000000",
                            "PrivateIpAddress": "10.186.136.127",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "000000000000",
                                        "PublicIp": "54.214.63.236"
                                    },
                                    "Primary": true,
                                    "PrivateIpAddress": "10.186.136.127"
                                }
                            ],
                            "SourceDestCheck": true,
                            "Status": "in-use",
                            "SubnetId": "subnet-949ce3fc",
                            "VpcId": "vpc-63af96d9"
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupId": "sg-0b9843e7a3d8d0519",
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
                    "InstanceId": "i-8a33d347e70f4d92f",
                    "ImageId": "ami-0c02fb55956c7d316",
                    "State": {
                        "Code": 16,
                        "Name": "running"
                    },
                    "PrivateDnsName": "ip-10-186-136-127.ec2.internal",
                    "PublicDnsName": "ec2-54-214-63-236.compute-1.amazonaws.com",
                    "StateTransitionReason": "",
                    "KeyName": "lab05-key",
                    "AmiLaunchIndex": 0,
                    "InstanceType": "t3.micro",
                    "LaunchTime": "2026-06-16T23:10:44+00:00",
                    "Placement": {
                        "GroupName": "",
                        "Tenancy": "default",
                        "AvailabilityZone": "us-east-1a"
                    },
                    "KernelId": "None",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "SubnetId": "subnet-949ce3fc",
                    "VpcId": "vpc-63af96d9",
                    "PrivateIpAddress": "10.186.136.127",
                    "PublicIpAddress": "54.214.63.236"
                }
            ]
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 describe-instance-attribute \
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
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 stop-instances --instance-ids $INSTANCE_ID
{
    "StoppingInstances": [
        {
            "InstanceId": "i-8a33d347e70f4d92f",
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
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 start-instances --instance-ids $INSTANCE_ID
{
    "StartingInstances": [
        {
            "InstanceId": "i-8a33d347e70f4d92f",
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
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 terminate-instances --instance-ids $INSTANCE_ID
{
    "TerminatingInstances": [
        {
            "InstanceId": "i-8a33d347e70f4d92f",
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
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 terminate-instances --instance-ids $INSTANCE_ID
{
    "TerminatingInstances": [
        {
            "InstanceId": "i-8a33d347e70f4d92f",
            "CurrentState": {
                "Code": 32,
                "Name": "shutting-down"
            },
            "PreviousState": {
                "Code": 48,
                "Name": "terminated"
            }
        }
    ]
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 delete-security-group --group-id $SG_ID

@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ 
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 delete-security-group --group-id $SG_ID

aws: [ERROR]: An error occurred (InvalidGroup.NotFound) when calling the DeleteSecurityGroup operation: The security group 'sg-0b9843e7a3d8d0519' does not exist
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal ec2 delete-key-pair --key-name lab05-key
{
    "Return": true
}
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal iam remove-role-from-instance-profile \
  --instance-profile-name app-instance-profile --role-name app-role
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ awslocal iam delete-instance-profile --instance-profile-name app-instance-profile
@laug80 ➜ /workspaces/cloud-foundations-lab (lab-05-GonzalezLau) $ 