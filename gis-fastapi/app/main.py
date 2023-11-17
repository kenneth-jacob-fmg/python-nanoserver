from fastapi import FastAPI, Header, status, HTTPException, Request, BackgroundTasks

from typing import Union
import hmac, hashlib, json, requests, ssl
import datetime, os
import re, configparser, logging
from app.models.upload import Upload
from app.models.custom_http_adapter import CustomHttpAdapter

logger = logging.getLogger("fastapi")

BYDA_FOLDER = "c:\\container_byda"
CONFIG_PATH = f'{BYDA_FOLDER}\\config\\config.ini'

config = configparser.ConfigParser()
config_section = os.environ['HOST_COMPUTERNAME']

with open(CONFIG_PATH, 'r') as config_file:
    config.read_file(config_file)

if(not (config_section in config)):
    logger.error(f'Configuration section {config_section} is not found - use "DEFAULT"')
    config_section="DEFAULT"

SERVER_ROOT_FOLDER = config[config_section]["ServerRootFolder"]
SIGNING_SECRET_KEY = config[config_section]["SigningSecretKey"].strip()
CLIENT_ID = config[config_section]["ClientId"].strip()
CLIENT_SECRET = config[config_section]["ClientSecret"].strip()
BASE_API_URL = config[config_section]["BaseAPIUrl"]
ARCGIS_PORTAL_USER = config[config_section]["ArcgisPortalUser"]
ARCGIS_PORTAL_PASSWORD = config[config_section]["ArcgisPortalPassword"]
ARCGIS_PORTAL_REFERER = config[config_section]["ArcgisPortalReferer"]
ARCGIS_PORTAL_TOKEN_URL = config[config_section]["ArcgisPortalTokenUrl"]
BYDA_GPTASK_URL = config[config_section]["BydaGpTaskUrl"]

REFERRAL_FOLDER = f'{BYDA_FOLDER}\\referrals'
SERVER_REFERRAL_FOLDER = f'{SERVER_ROOT_FOLDER}\\referrals'
#SCRIPT_FILE_PATH = f'{BYDA_FOLDER}\\script\\{config[config_section]["ScriptName"]}'
LOG_PATH = f'{BYDA_FOLDER}\\logs'
SSL_PATH = f'{BYDA_FOLDER}\\ssl\\{config[config_section]["FortescueSSLCertChain"]}'

app = FastAPI()

def execute_thread(req_info):
    
    filename = f'{req_info[0]["uuid"]}.json'
    message = req_info[0]["message"]

    sequence_number = message["sequenceNumber"]
    logger.info(f'SEQ_NO:{sequence_number}')

    job_number = message["Enquiry"]["jobNumber"]
    logger.info(f'Job_Number:{job_number}')

    applicant = f'{message["Enquiry"]["User"]["firstName"]} {message["Enquiry"]["User"]["lastName"]}'
    logger.info(f'Applicant:{applicant}')

    registered_email = f'{message["Enquiry"]["User"]["registeredEmail"]}'
    logger.info(f'Registered email:{registered_email}')

    request_payload = json.dumps(message, separators=(',', ':'))

    current_year = datetime.datetime.today().year
    referral_folder_name_template = config[config_section]["ReferralFolderNameTemplate"].replace("<YEAR>", str(current_year))
    container_folder = f'{REFERRAL_FOLDER}\\{referral_folder_name_template}\\'
    server_folder = f'{SERVER_REFERRAL_FOLDER}\\{referral_folder_name_template}\\'
    container_filepath = container_folder + filename
    server_filepath = server_folder + filename
    logger.info(f'GEOJSON_File:{server_filepath}')

    if(not os.path.isdir(container_folder)):
        os.makedirs(container_folder)

    with open(container_filepath, 'w') as file:
        file.write(request_payload)

    # Note: change from invoke python script to gptask instead
    #call(["python", SCRIPT_FILE_PATH, req_info[0]["uuid"]])

    logger.info(f'POST - {ARCGIS_PORTAL_TOKEN_URL}')
    payload = {
        "f":"json",
        "username":ARCGIS_PORTAL_USER,
        "password":ARCGIS_PORTAL_PASSWORD,
        "referer":ARCGIS_PORTAL_REFERER,
        "expiration":60
    }

    # --------
    # NOTE: Applied workaround
    # https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
    # --------

    #token_result = requests.post(ARCGIS_PORTAL_TOKEN_URL, verify=f'{SSL_PATH}', data=payload)
    token_result = get_legacy_session().post(ARCGIS_PORTAL_TOKEN_URL, data=payload)

    logger.info(token_result)
    token_req_info = token_result.json()

    logger.info(f'POST - {BYDA_GPTASK_URL}')
    payload = {
                    "token":token_req_info["token"],
                    "SEQ_NO":sequence_number,
                    "Job_Number":job_number,
                    "Applicant":applicant,
                    "GEOJSON_File":server_filepath
                    }
    #gptask_result = requests.post(BYDA_GPTASK_URL, verify=f'{SSL_PATH}', data=payload)
    gptask_result = get_legacy_session().post(BYDA_GPTASK_URL, data=payload)

    logger.info(gptask_result)
    gptask_req_info = gptask_result.json()
    logger.info(gptask_req_info)

@app.get("/referral")
async def referral_get():
    return {}

@app.post("/referral")
async def referral_post(background_tasks: BackgroundTasks, x_swx_signature: Union[str, None] = Header(default=None),
                         request: Request = None):

    # request.json() returns dictionary object
    req_info = await request.json()
    # !NOTE: default json.dumps introduce single space to some separators that causes signature verification mismatch
    request_body = json.dumps(req_info, separators=(',', ':'))

    signature = hmac.new(SIGNING_SECRET_KEY.encode(), request_body.encode(), hashlib.sha256).hexdigest()
    #logger.info(signature);
    if(not (x_swx_signature == f'sha256={signature}')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f'Unauthorized usage.')

    background_tasks.add_task(execute_thread, req_info)

    return {}

@app.post("/upload")
async def upload(request: Upload = None):
    
    logger.info(request)
    pattern = '[\w-]+?(?=\.pdf)'
    filename = re.search(pattern, request.path)
 
    current_year = datetime.datetime.today().year
    referral_folder_name_template = config[config_section]["ReferralFolderNameTemplate"].replace("<YEAR>", str(current_year))
    filepath = f'{REFERRAL_FOLDER}\\{referral_folder_name_template}\\{filename.group()}\\{filename.group()}.pdf'

    # Validate filepath
    logger.info(filepath)
    if not os.path.exists(filepath):
        message = f'PDF {filepath} does not exist'
        logger.error(message)
        return {"status": "Failed", "message": message}

    # Read pdf as binary content
    with open(filepath, mode='rb') as file:
        fileContent = file.read()

    # Authenticate SmarterWX
    auth_result = requests.post(f'{BASE_API_URL}/community/auth/tokens', 
                    json = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET})
    auth_rec_info = auth_result.json()

    # Query Referral Detail
    referral_detail_url = f'{BASE_API_URL}/enquiries/{request.enquiryId}/referrals/{request.referralId}'
    referral_detail_result = requests.get(referral_detail_url,
                            headers={'Authorization':auth_rec_info["access_token"]})

    # Validate existing referral detail
    if referral_detail_result.status_code == 400:
        message = f'Referral detail not found - {referral_detail_url}'
        logger.error(message)
        return {"status": "Failed", "message": message}

    # Request pdf upload location
    upload_result = requests.post(f'{BASE_API_URL}/system/uploads', 
                    json = {'name': f'{filename.group()}.pdf', 'mimeType': 'application/pdf'},
                    headers={'Authorization':auth_rec_info["access_token"]})

    upload_rec_info = upload_result.json()
    logger.info(upload_rec_info)

    # Put pdf file to designated AWS S3 Url
    put_file_result = requests.put(upload_rec_info["url"], data=fileContent)
    logger.info(f'PUT Request - {put_file_result}')

    # Assign response fileid to the referral detail  
    add_response_result = requests.post(f'{BASE_API_URL}/enquiries/{request.enquiryId}/referrals/{request.referralId}/responses',
                            json = {'body': f"{request.emailBodyContent}", "Files": [{"id": upload_rec_info["id"]}]},
                            headers={'Authorization':auth_rec_info["access_token"]})

    add_response_rec_info = add_response_result.json()
    logger.info(add_response_rec_info)

    status = "Success"

    return {
        "status" : status,
        "message": ""
    }

@app.post("/upload-package")
async def upload_package(request: Upload = None):
    
    logger.info(request)
    pattern = '[\w-]+?(?=\.zip)'
    filename = re.search(pattern, request.path)
 
    current_year = datetime.datetime.today().year
    referral_folder_name_template = config[config_section]["ReferralFolderNameTemplate"].replace("<YEAR>", str(current_year))
    filepath = f'{REFERRAL_FOLDER}\\{referral_folder_name_template}\\{filename.group()}\\{filename.group()}.zip'

    # Validate filepath
    logger.info(filepath)
    if not os.path.exists(filepath):
        message = f'Zip {filepath} does not exist'
        logger.error(message)
        return {"status": "Failed", "message": message}

    # Read pdf as binary content
    with open(filepath, mode='rb') as file:
        fileContent = file.read()

    # Authenticate SmarterWX
    auth_result = requests.post(f'{BASE_API_URL}/community/auth/tokens', 
                    json = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET})
    auth_rec_info = auth_result.json()

    # Query Referral Detail
    referral_detail_url = f'{BASE_API_URL}/enquiries/{request.enquiryId}/referrals/{request.referralId}'
    referral_detail_result = requests.get(referral_detail_url,
                            headers={'Authorization':auth_rec_info["access_token"]})

    # Validate existing referral detail
    if referral_detail_result.status_code == 400:
        message = f'Referral detail not found - {referral_detail_url}'
        logger.error(message)
        return {"status": "Failed", "message": message}

    # Request pdf upload location
    upload_result = requests.post(f'{BASE_API_URL}/system/uploads', 
                    json = {'name': f'{filename.group()}.zip', 'mimeType': 'application/zip'},
                    headers={'Authorization':auth_rec_info["access_token"]})

    upload_rec_info = upload_result.json()
    logger.info(upload_rec_info)

    # Put pdf file to designated AWS S3 Url
    put_file_result = requests.put(upload_rec_info["url"], data=fileContent)
    logger.info(f'PUT Request - {put_file_result}')

    # Assign response fileid to the referral detail  
    add_response_result = requests.post(f'{BASE_API_URL}/enquiries/{request.enquiryId}/referrals/{request.referralId}/responses',
                            json = {'body': f"{request.emailBodyContent}", "Files": [{"id": upload_rec_info["id"]}]},
                            headers={'Authorization':auth_rec_info["access_token"]})

    add_response_rec_info = add_response_result.json()
    logger.info(add_response_rec_info)

    status = "Success"

    return {
        "status" : status,
        "message": ""
    }

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session