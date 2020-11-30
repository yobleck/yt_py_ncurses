#initiliaze youtube api
import os, sys;

import google_auth_oauthlib.flow;
import googleapiclient.discovery;
import googleapiclient.errors;
import google.oauth2.credentials;
import google.auth.transport.requests;


def Init():
    cwd = sys.path[0] + "/";
    scopes = ["https://www.googleapis.com/auth/youtube"]; #change youtube.readonly to just youtube
    credentials_file = cwd + "json/credentials.json"; #make this come from config file? also encrypt it?
    
    # Disable OAuthlib's HTTPS verification when running locally.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"; # *DO NOT* leave this option enabled in production.

    api_service_name = "youtube";
    api_version = "v3";
    client_secrets_file = cwd + "json/client_secret_915368223513-6bt98h496rv56tj4r2uq57te33i7he3p.apps.googleusercontent.com.json";

    # Get client key and secrets and create an API client
    #flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        #client_secrets_file, scopes);
    
    
    if(not os.path.isfile(credentials_file)): # no credentials file?
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes);
        credentials = flow.run_local_server(); #credentials = flow.run_console();
        cred_json = credentials.to_json();
        print("cred_json:\n", cred_json);
        f = open(cwd + "json/credentials.json","w");
        f.write(cred_json);
        f.close();
    
    #get credentials/tokens from file
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(credentials_file,scopes);
    
    if(credentials.expired): #refresh access token if expired and save to json
        credentials.refresh(google.auth.transport.requests.Request()); # does none need to be there?
        cred_json = credentials.to_json();
        #print("cred_json:\n", cred_json);
        f = open(cwd + "json/credentials.json","w");
        f.write(cred_json);
        f.close();
    
    #actual youtube object from which data is retrieved
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials);
    
    return youtube;
