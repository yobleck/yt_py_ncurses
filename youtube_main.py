#main file that handles gui, user input and maybe authentication
import time, os, sys, glob;
import curses, locale, re; 
import yt_api_init, json, subprocess;
import read_settings;
from distutils.util import strtobool;


cwd = sys.path[0] + "/";
#logging tool
#f = open(cwd + "log.txt","w"); f.write(str(sys.path)); f.close();

#
def loading_scr(scr, mes):
    scr.addstr(0,0,mes);
    scr.refresh();


#TODO: add colors

def main(main_scr):
    ###initialization of curses
    curses.start_color();
    curses.use_default_colors();
    curses.curs_set(0);
    term_h, term_w = main_scr.getmaxyx();
    main_scr.nodelay(True);
    main_scr.keypad(True);
    
    #error and clean exit function
    def except_func(error_msg):
        loading_scr(main_scr, "Something went wrong. Attempting clean exit...");
        main_scr.refresh();
        time.sleep(2);
        curses.endwin();
        return error_msg;
   
   
    ###api initialization###
    loading_scr(main_scr,"Loading API's...");
    try:
        yt_api = yt_api_init.Init(); #still used for like/dislike
        import yt_api_request;
    except Exception as e:
        return str(e) + "\n" + except_func("youtube api error: unable to load api");
    
    
    
    ###api information download###
    loading_scr(main_scr,"Loading YouTube Channel Info...");
    try:
        my_channel_info= yt_api_request.user_channel_info();
    except Exception as e:
        return str(e) + "\n" + except_func("youtube api error: could not retrieve user channel info");
    
    loading_scr(main_scr,"Loading YouTube Subscription Info...");
    try:
        yt_subs, subs_vid_count, sub_has_new_vid = yt_api_request.user_subs();
    except Exception as e:
        return str(e) + "\n" + except_func("youtube api error: could not retrieve subscription information");
    num_subs = len(yt_subs);
    
    
    
    ###misc initialization###
    loop = True;
    chnl_uplds = [];
    ratings = {"108":"like", "100":"dislike", "110":"none"}; # maps user input to video rating action
    max_com = 50;
    comments = [];
    
    ###read from settings file###
    try:
        max_vids = int( read_settings.get_setting("max_videos", [str(i) for i in list(reversed(range(50,1050,50)))] ) );
        settings_bool = ["True","False"];
        show_e = bool( strtobool( read_settings.get_setting("show_emoji", settings_bool) ));
        if(not show_e):
            e_filter = re.compile(r"[\U0000231A-\U00002B55\U0001F004-\U0001FAD6\U0001F170-\U0001F6F3\U0001F1E6-\U0001F1FC\U0001F3FB-\U0001F3FF]+");
        else:
            e_filter = re.compile(r"q^"); #this regex matches nothing and is efficient unless string ends in lots of "q"
        is_android = bool( strtobool( read_settings.get_setting("is_android", settings_bool) ));
    except Exception as e:
        return str(e) + "\n" + except_func("could not read settings.ini. make sure variable names and values are correct");
    
    
    
    ###initialization of screens
    home_scr = curses.newwin(term_h,term_w,0,0);
    info_scr = curses.newwin(term_h,term_w,0,0);
    sub_pad = curses.newpad(num_subs+2,term_w);
    chnl_pad = curses.newpad(max_vids+2,term_w);
    vid_scr = curses.newwin(term_h,term_w,0,0);
    com_pad = curses.newpad(max_com+2,term_w);
    
    #format: if len = 1 then [win]. if len > 1 then [pad, start_y, start_x, max_length, select_pos, list_var]
    fake_panel = [[home_scr], [info_scr], [sub_pad,0,0,num_subs,0,yt_subs], [chnl_pad,0,0,max_vids,0,chnl_uplds], [vid_scr], [com_pad,0,0,max_com,0,comments]];
    in_focus = fake_panel[0];
    
    
    
    ###screen set up###
    home_scr.addstr(0,0,("Welcome to the YouTube nCurses Browser\n"
                    "Made by: Yobleck\n\n"
                    "Controls:\n"
                    "\'i\' = Goto Your Channel Info\n"
                    "\'s\' = Goto Your Subscriptions\n"
                    "\'Enter\' = Select Channel from Subs or Video from Channel\n"
                    "\'Backspace\' = Go Back a Page\n"
                    "\'Space Bar\' = Play Video with mpv + youtube-dl Streaming\n"
                    "\'l,d,n\' = Like/Dislike/None\n"
                    "\'t\' = dl and View Video Thumbnail\n"
                    "note: you can go back to subs anytime\nbut to go back to a channel/video you must go the same way as the first time"));
    home_scr.refresh();
    
    #yt landing page with user channel info
    info_scr.addnstr(0,0, "Channel Info:", term_w, curses.A_UNDERLINE);
    info_scr.addstr(1,0, my_channel_info["items"][0]["snippet"]["title"], curses.A_UNDERLINE);
    info_scr.addnstr(2,0, "Channel ID: " + my_channel_info["items"][0]["id"], term_w);
    info_scr.addnstr(3,0, "Channel Birthday: " + my_channel_info["items"][0]["snippet"]["publishedAt"], term_w);
    info_scr.addnstr(4,0, "Country: " + my_channel_info["items"][0]["snippet"]["country"], term_w);
    info_scr.addstr(5,0, "Thumbnail: " + my_channel_info["items"][0]["snippet"]["thumbnails"]["default"]["url"]);
    
    #scrollable and clickable list of user subscriptions
    sub_pad.addstr(0,0, "My YT Subscriptions", curses.A_ITALIC | curses.A_UNDERLINE | curses.A_BOLD); #TODO: add notification of new videos on this page?
    for num, sub in enumerate(yt_subs):
        sub_pad.addnstr(num+1,0, re.sub(e_filter, " ", sub["title"]), term_w);
    
    
    
    while(loop):
        
        usr_input = main_scr.getch();
        if(usr_input == 27):
            loop = False;
        
        
        if(usr_input == 105): #i show user channel info on screen
            #is_visible[0] = False;
            in_focus = fake_panel[1]; #is_visible[1] = True; 
        
        if(usr_input == 115): #s show user subscriptions page
            in_focus = fake_panel[2]; #is_visible[2] = True; 
            #is_visible[0] = False; is_visible[1] = False; is_visible[3] = False; is_visible[4] = False;
            #subs page can be accessed from anywhere. hence hiding all other pages
        
        
        ###arrow key nav###
        if(usr_input == 258 and len(in_focus) > 1 and in_focus[4] < in_focus[3]-1): #scroll pad down with over scroll prevention
            in_focus[0].addnstr(in_focus[4]+1,0, re.sub(e_filter, " ", in_focus[5][in_focus[4]]["title"]), term_w);
            in_focus[4] += 1;
            in_focus[0].addnstr(in_focus[4]+1,0, re.sub(e_filter, " ", in_focus[5][in_focus[4]]["title"]), term_w, curses.A_REVERSE);
            if(in_focus[4] > in_focus[1]+term_h-3):
                in_focus[1] += 1;
        
        if(usr_input == 259 and len(in_focus) > 1 and in_focus[4] > 0): #scroll pad up
            in_focus[0].addnstr(in_focus[4]+1,0, re.sub(e_filter, " ", in_focus[5][in_focus[4]]["title"]), term_w);
            in_focus[4] -= 1;
            in_focus[0].addnstr(in_focus[4]+1,0, re.sub(e_filter, " ", in_focus[5][in_focus[4]]["title"]), term_w, curses.A_REVERSE);
            if(in_focus[4] < in_focus[1]):
                in_focus[1] -= 1;
        
        
        ###Enter###
        if(usr_input == 10):
            if(in_focus == fake_panel[2]): #selecting channel to display uploads
                #get videos from yt api
                try:
                    video_list = yt_api_request.videos(yt_subs[in_focus[4]]["resourceId"]["channelId"], max_vids); #max_vids
                except Exception as e:
                    fake_panel[3][0].erase(); fake_panel[3][0].refresh(0,0,0,0,term_h-1,term_w);
                    return str(e) + "\n" + except_func("youtube api error: unable to get channel uploads");
                
                #prepare channel screen for drawing videos by resetting variables
                fake_panel[3][0].erase();
                fake_panel[3][1], fake_panel[3][2], fake_panel[3][4] = [0]*3;  #TODO: show num vids displayed out of total
                fake_panel[3][0].addnstr(0,0, "Channel: " + yt_subs[in_focus[4]]["title"], term_w, curses.A_ITALIC | curses.A_UNDERLINE | curses.A_BOLD);
                fake_panel[3][5] = [];
                
                #add list of videos to screen list
                fake_panel[3][5] = list(video_list);
                fake_panel[3][3] = len(fake_panel[3][5]); #max length for scrolling
                
                #draw videos on channel screen
                for num, vid in enumerate(fake_panel[3][5]):
                    fake_panel[3][0].addnstr(num+1,0, re.sub(e_filter, " ", vid["title"]), term_w);
                in_focus = fake_panel[3]; #is_visible[3] = True; is_visible[2] = False;
            
            
            elif(in_focus == fake_panel[3]):
                fake_panel[4][0].erase();
                fake_panel[4][0].addnstr(0,0,"Video: " + in_focus[5][in_focus[4]]["title"], term_w, curses.A_ITALIC | curses.A_UNDERLINE | curses.A_BOLD);
                try:
                    #fake_panel[4][0].addnstr(2,0,"Thumbnail: " + in_focus[5][in_focus[4]]["thumbnails"]["maxres"]["url"], term_w);
                    thumb_url = in_focus[5][in_focus[4]]["thumbnails"]["maxres"]["url"];
                except:
                    #fake_panel[4][0].addnstr(2,0,"Thumbnail: " + in_focus[5][in_focus[4]]["thumbnails"]["default"]["url"], term_w);
                    thumb_url = in_focus[5][in_focus[4]]["thumbnails"]["default"]["url"];
                fake_panel[4][0].addnstr(2,0,"Thumbnail: " + thumb_url, term_w);
                
                #draw video url
                fake_panel[4][0].addnstr(3,0,"url: https://www.youtube.com/watch?v=" + in_focus[5][in_focus[4]]["resourceId"]["videoId"], term_w);
                fake_panel[4][0].addnstr(5,0,"Desc: " + in_focus[5][in_focus[4]]["description"].replace("\n"," "), term_w*(term_h-8));
                
                #draw like/dislike
                fake_panel[4][0].addnstr(fake_panel[4][0].getmaxyx()[0]-1,0, "Like/Dislike status: " + yt_api.videos().getRating(id=in_focus[5][in_focus[4]]["resourceId"]["videoId"]).execute()["items"][0]["rating"], term_w);
                in_focus = fake_panel[4]; #is_visible[4] = True; is_visible[3] = False;
        
        
        
        if(usr_input == 32 and in_focus == fake_panel[4]): #space bar to play video
            if(is_android):
                subprocess.run([ "youtube-dl", "https://www.youtube.com/watch?v="+fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"]], stdout=subprocess.DEVNULL);
                subprocess.run([ "termux-share", "$(youtube-dl", "--get-filename", "https://www.youtube.com/watch?v="+fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"]+")"], stdout=subprocess.DEVNULL);
            else: #linux and hopefully windows as well
                subprocess.run([ "mpv", "https://www.youtube.com/watch?v="+fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"] ], stdout=subprocess.DEVNULL);
        
        
        
        if(usr_input in [108,100,110] and in_focus == fake_panel[4]): #like/dislike/none with l,d,n
            yt_api.videos().rate(id=fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"], rating=ratings[str(usr_input)]).execute();
            fake_panel[4][0].addnstr(fake_panel[4][0].getmaxyx()[0]-1,0,"Like/Dislike status: " + ratings[str(usr_input)] + "   ", term_w);
        
        
        if(usr_input == 116 and in_focus == fake_panel[4]): #view thumbnail
            subprocess.run(["wget", "-O", cwd + "thumbnails/thumb.jpg", thumb_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL);
            subprocess.run(["display", cwd + "thumbnails/thumb.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL);
            os.remove(cwd + "thumbnails/thumb.jpg");
        
        
        if(usr_input == 99 and in_focus == fake_panel[4]): #TODO:comment section
            pass;
        
        
        if(usr_input == 127): #backspace to go back a page
            if(in_focus == fake_panel[5]): #comments to video
                in_focus = fake_panel[4];
            elif(in_focus == fake_panel[4]): #video to channel
                in_focus = fake_panel[3];
            elif(in_focus == fake_panel[3]): #channels to subs
                in_focus = fake_panel[2];
            elif(in_focus in [fake_panel[1], fake_panel[2]]): #subs and info to home
                in_focus = fake_panel[0];
        
        
        
        #redraw loop checks what is visible and draws in the correct order. slow but nothing else tried worked.
        if(usr_input != -1): #only updates when user interacts with it. allows for text selection with mouse
            for x in range(5):
                if(fake_panel[x] == in_focus):#if(is_visible[x]):
                    fake_panel[x][0].redrawwin();
                    try:
                        fake_panel[x][0].refresh(); #windows
                    except curses.error:
                        fake_panel[x][0].refresh(fake_panel[x][1],fake_panel[x][2], 0,0, term_h-1,term_w); #pads
        
        time.sleep(0.01);
    #end while loop
    
    
    return "clean exit, no errors";
#end main

###actual running of code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '');
    os.environ.setdefault('ESCDELAY', '25'); #why do I not need this in gtav_radio.py?
    return_code = curses.wrapper(main);
    if(len(sys.argv)>1):
        if(sys.argv[1] in ["v","-v","--v","verbose","--verbose"]):
            print(return_code);
