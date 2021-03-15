# Schema Terraform Configuration

## Requirements
1. Download Terraform

    The configuration files are compatible with version v0.14.6
    ```
    $ terraform version
    Terraform v0.14.6
    + provider registry.terraform.io/hashicorp/aws v3.31.0
    ```
2. The route53 hosted zones should be pre-created and their name servers should be configured by the owner team of the parent domain.


Environment|Domain|Parent Domain|Owner
--- | --- | --- | --- 
prod|schema.humancellatlas.org|humancellatlas.org| Sanger - Send an email to `Servicedesk@sanger.ac.uk` mailing list and mark message subject with `[FAO core IMT]` <br/> Please ask Laura Clarke, laura@ebi.ac.uk for details.
staging|(temporary)schema.staging.data.humancellatlas.org|data.humancellatlas.org| HCA DCP Data Portal/Azul Team - Send a message on HCA Slack Workspace to `hannes@ucsc.edu` as he's the one who's been doing it in the past.
dev|(temporary)schema.dev.data.humancellatlas.org|data.humancellatlas.org| HCA DCP Data Portal/Azul Team - same instruction as above
integration| (temporary) schema.integration.archive.data.humancellatlas.org|archive.data.humancellatlas.org|Ingest devs own this parent domain. No need to point the name servers. 

## To do
1. Add tags to AWS resources

## Create or update the schema instance
1. Go to directory containing Terraform configuration files
    ```
    cd terraform
    ```
1. Initialize working directory
    ```
    source init.sh integration # or dev, staging, prod
    ```
1. (If update) Update the config or variable files (e.g. `.tf` files or `.tfvars`)

1. Apply the configuration
    ```
    terraform apply -var-file=integration.tfvars # or dev, staging, prod
    ```
1. Confirm the resources to be created or updated.

## Destroy

Run and confirm the resources to be deleted.
```
terraform destroy -var-file=integration.tfvars # or dev, staging, prod
```