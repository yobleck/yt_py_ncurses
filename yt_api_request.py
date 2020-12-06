import os, sys, json;
import yt_api_init;

cwd = sys.path[0] + "/";

yt_api = yt_api_init.Init();

###
def user_channel_info():
    return yt_api.channels().list(mine=True, part="snippet").execute();

###
def user_subs():
    if(len(os.listdir(cwd + "json/yt_subs/")) == 0):
        num_subs = yt_api.subscriptions().list(mine=True, part="contentDetails", maxResults=1).execute()["pageInfo"]["totalResults"];
        f = open(cwd + "json/yt_subs/num_subs","w"); f.write(str(num_subs)); f.close();
        
        yt_sub_pages = [];#sub info pages because api request max is 50 items
        yt_sub_pages.append( yt_api.subscriptions().list(mine=True, part="snippet", order="alphabetical", maxResults=50).execute() );
        
        for i in range((num_subs//50)):
            yt_sub_pages.append( yt_api.subscriptions().list(mine=True, part="snippet", order="alphabetical", #sub info more pages
                                                        maxResults=50, pageToken=yt_sub_pages[i]["nextPageToken"]).execute() );
        
        
        f = open(cwd + "json/yt_subs/subs","w");
        yt_subs = [];
        for i in yt_sub_pages:
            for j in i["items"]:
                yt_subs.append(j["snippet"]);
                json.dump(j["snippet"],f);
                f.write("\n");
        f.close();
    else: #open subscription cache file ane read subs
        f = open(cwd + "json/yt_subs/subs","r");
        yt_subs = [json.loads(x) for x in f.readlines()];
    
    return yt_subs;

###
def videos(channel_id, max_videos):
    channel = yt_api.channels().list(id=channel_id, part="contentDetails").execute();
    video_pages = [];
    video_pages.append( yt_api.playlistItems().list(playlistId=channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"], 
                                                    part="snippet",maxResults=50).execute() );
    
    for i in range( (min(max_videos,video_pages[0]["pageInfo"]["totalResults"])//50)-1 ): #TODO: fix rounding error
        video_pages.append( yt_api.playlistItems().list(playlistId=channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"], 
                                                        part="snippet",maxResults=50, pageToken=video_pages[i]["nextPageToken"]).execute() );
    
    #TODO: add most recent video id to list that is checked on next startup to look for new videos?
    
    video_list = [];
    for i in video_pages:
        for j in i["items"]:
            video_list.append(j);
    
    
    return video_list; #video_pages[0]["items"][0];
