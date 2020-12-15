import os, sys, json;
import yt_api_init, read_settings;
from distutils.util import strtobool;

cwd = sys.path[0] + "/";

yt_api = yt_api_init.Init();
check_new_vids = bool(strtobool(read_settings.get_setting("check_new_vids", ["True","False"])));

##########
def user_channel_info():
    return yt_api.channels().list(mine=True, part="snippet").execute();



##########
def user_subs():
    #getting number of subscriptions from both api and cache file
    num_subs = yt_api.subscriptions().list(mine=True, part="contentDetails", maxResults=1).execute()["pageInfo"]["totalResults"];
    if(os.path.isfile(cwd + "json/yt_subs/num_subs")):
        f = open(cwd + "json/yt_subs/num_subs","r"); temp_num_subs = int(f.readline()); f.close();
    else:
        temp_num_subs = 0;
    
    
    if(len(os.listdir(cwd + "json/yt_subs/")) == 0 or not os.path.isfile(cwd + "json/yt_subs/subs") or 
       num_subs != temp_num_subs or check_new_vids):
        
        f = open(cwd + "json/yt_subs/num_subs","w"); f.write(str(num_subs)); f.close(); #write num subs to file
        
        
        #get list of number of videos per subscription
        if(check_new_vids):
            if(os.path.isfile(cwd + "json/yt_subs/num_subs")):
                f = open(cwd + "json/yt_subs/subs_vid_count","r");
                temp_num_vids = [int(i) for i in f.readlines()];
                f.close();
            else:
                temp_num_vids = [0]*num_subs;
        
        
        yt_sub_pages = [];#sub info pages because api request max is 50 items
        temp_page_token = None;
        while(True):
            yt_sub_pages.append( yt_api.subscriptions().list(mine=True, part="snippet,contentDetails", order="alphabetical", #sub info more pages
                                                             maxResults=50, pageToken=temp_page_token).execute() );
            if("nextPageToken" in yt_sub_pages[-1]):
                temp_page_token = yt_sub_pages[-1]["nextPageToken"];
            else:
                break;
        
        
        #generate output lists and write them to files
        f = open(cwd + "json/yt_subs/subs","w"); f2 = open(cwd + "json/yt_subs/subs_vid_count","w");
        yt_subs = [];
        subs_vid_count = [];
        for i in yt_sub_pages:
            for j in i["items"]:
                yt_subs.append(j["snippet"]); #subscription channelId and title
                json.dump(j["snippet"],f);
                f.write("\n");
                
                subs_vid_count.append(j["contentDetails"]["totalItemCount"]); #subscription video count
                f2.write(str(j["contentDetails"]["totalItemCount"]) + "\n");
        f.close(); f2.close();
        
        
        #compare temp_num_vids to subs_vid_count and generate list has_new_vid
        if(check_new_vids):
            has_new_vid = [];
            for i in range(len(subs_vid_count)):
                if(subs_vid_count[i] == temp_num_vids[i]):
                    has_new_vid.append(False);
                else:
                    has_new_vid.append(True);
        else:
            has_new_vid = [False]*num_subs;
    
    
    else: #open subscription cache file and read subs and vid count
        f = open(cwd + "json/yt_subs/subs","r"); f2 = open(cwd + "json/yt_subs/subs_vid_count","r");
        yt_subs = [json.loads(x) for x in f.readlines()];
        subs_vid_count = f2.readlines();
        f.close(); f2.close();
        has_new_vid = [False]*num_subs;
    #TODO: how to read subs_vid_count from api efficiently, and return difference from cache to indicate new videos?
    return (yt_subs, subs_vid_count, has_new_vid);



##########
def videos(channel_id, max_videos):
    channel = yt_api.channels().list(id=channel_id, part="contentDetails").execute();
    video_pages = [];
    temp_page_token = None;
    while(True):
        video_pages.append( yt_api.playlistItems().list(playlistId=channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"], 
                                                        part="snippet",maxResults=50, pageToken=temp_page_token).execute() );
        if("nextPageToken" in video_pages[-1]):
            temp_page_token = video_pages[-1]["nextPageToken"];
        else: #if channel has less than 50 or max_videos
            break;
        if(len(video_pages) >= max_videos//50): #if channel had more than max_videos then cut off.   maybe put above other if?
            break;
    
    #TODO: add most recent video id to list that is checked on next startup to look for new videos?
    
    video_list = [];
    for i in video_pages:
        for j in i["items"]:
            video_list.append(j["snippet"]);
    
    
    return video_list; #video_pages[0]["items"][0];



##########
def comments(video_id, max_com): #TODO: Requires force-ssl oauth scope or use open api key
    com_list = yt_api.commentThreads().list(videoId=video_id, maxResults=max_com, part="snippet", order="relevance", 
                                            textFormat="plainText").execute();
    print(com_list["items"][0]);
