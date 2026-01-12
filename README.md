# startup-terraform-phases (EVAL)

Containerized demo generator for **phase-based Terraform repo bundles**:
- preseed
- seed
- series-a
- series-b

**EVAL constraints**:
- AWS-only (--cloud aws)
- plan-only (no apply automation)
- no real credentials
- demo evidence artifacts only

## Build
\\\
docker build -t ghcr.io/boiindil/startup-terraform-phases:latest -t ghcr.io/boiindil/startup-terraform-phases:0.1.0 .
\\\

## Run
\\\
docker run --rm -v "\C:\Users\winfr\Downloads/out:/out" ghcr.io/boiindil/startup-terraform-phases:latest generate --phase seed --cloud aws --region eu-central-1
\\\

Outputs:
- /out/bundle
- /out/MANIFEST.json
- /out/EVIDENCE/ (Series A/B only)