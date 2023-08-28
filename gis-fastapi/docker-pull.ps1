$EACH_PYTHON_VERSION='3.11.5'
$EACH_WIN_VERSION='1809'
$IMAGE_TAG="${EACH_PYTHON_VERSION}_${EACH_WIN_VERSION}"
$CONTAINER_REGISTRY="fmgaksacr.azurecr.io"

docker pull $CONTAINER_REGISTRY/fastapi-nanoserver:$IMAGE_TAG

