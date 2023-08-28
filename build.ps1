$EACH_PYTHON_VERSION='3.11.5'
$EACH_WIN_VERSION='1809'
$IMAGE_TAG="${EACH_PYTHON_VERSION}_${EACH_WIN_VERSION}"

$TARGET_PYTHON_PIP_VERSION='23.2.1'
$TARGET_PYTHON_GET_PIP_URL='https://bootstrap.pypa.io/get-pip.py'

docker build `
    -t fmgaksacr.azurecr.io/python-nanoserver:$IMAGE_TAG `
    --build-arg WINDOWS_VERSION=$EACH_WIN_VERSION `
    --build-arg PYTHON_VERSION=$EACH_PYTHON_VERSION `
    --build-arg PYTHON_RELEASE=$EACH_PYTHON_VERSION `
    --build-arg PYTHON_PIP_VERSION=$TARGET_PYTHON_PIP_VERSION `
    --build-arg PYTHON_GET_PIP_URL=$TARGET_PYTHON_GET_PIP_URL `
    .

docker container prune
docker image prune
