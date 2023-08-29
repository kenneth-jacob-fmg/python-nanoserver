$EACH_PYTHON_VERSION='3.11.5'
$EACH_WIN_VERSION='1809'
$IMAGE_TAG="${EACH_PYTHON_VERSION}_${EACH_WIN_VERSION}"
$CONTAINER_REGISTRY="fmgaksacr.azurecr.io"

$FOLDER_BYDA="D:\byda"
$FOLDER_REFERRALS="${FOLDER_BYDA}\referrals"
$FOLDER_SCRIPT="${FOLDER_BYDA}\script"
$FOLDER_LOGS="${FOLDER_BYDA}\logs"
$FOLDER_SSL="${FOLDER_BYDA}\ssl"
$FILE_CONFIG="${FOLDER_BYDA}\config\config.ini"

$VOLUME_BYDA=$FOLDER_BYDA+":c:\container_byda"

if ( -not (Test-Path -Path $FOLDER_REFERRALS -PathType Container) ) { "Referral folder is missing"; Exit }
if ( -not (Test-Path -Path $FOLDER_SCRIPT -PathType Container) ) { "Script folder is missing"; Exit }
if ( -not (Test-Path -Path $FOLDER_LOGS -PathType Container) ) { "Logs folder is missing"; Exit }
if ( -not (Test-Path -Path $FOLDER_SSL -PathType Container) ) { "SSL folder is missing"; Exit }
if ( -not (Test-Path -Path $FILE_CONFIG -PathType Leaf) ) { "Config file is missing"; Exit }

docker run --rm -p 8000:8432 `
    -v $VOLUME_BYDA `
    -e HOST_COMPUTERNAME=$env:computername `
    -e SSL_CERTFILE=pthgisgate08.fmg.local.crt `
    -e SSL_KEYFILE=pthgisgate08.fmg.local.key `
    $CONTAINER_REGISTRY/fastapi-nanoserver:$IMAGE_TAG