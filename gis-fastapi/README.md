# fastapi
 
 ## Build Container

- Verify which Windows Server version the container is running in.
- Execute `docker pull mcr.microsoft.com/windows/servercore:1809`
- Execute `docker pull mcr.microsoft.com/windows/nanoserver:1809`
- In the python-nanoserver-fork folder, execute `build.ps1` to build the python-nanoserver image
- In the gis-fastapi folder, execute `build.ps1` to build the fastapi-nanoserver image

## Container Registry

- Run `az login`
- Run `az acr login --name fmgaksacr`
- Check push version before pushing to container registry
- Run `docker-push.ps1`


