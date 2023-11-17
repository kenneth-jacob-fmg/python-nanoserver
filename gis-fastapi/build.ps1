$EACH_PYTHON_VERSION='3.11.5'
$EACH_WIN_VERSION='1809'
$BUILD_VERSION='v2'
$IMAGE_TAG="${EACH_PYTHON_VERSION}_${EACH_WIN_VERSION}_${BUILD_VERSION}"
$CONTAINER_REGISTRY="fmgaksacr.azurecr.io"

docker build `
    -t $CONTAINER_REGISTRY/fastapi-nanoserver:$IMAGE_TAG `
    .

docker image prune -f