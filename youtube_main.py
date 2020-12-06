#main file that handles gui, user input and maybe authentication
import time, os, sys;
import curses, locale, re; 
import yt_api_init, json, subprocess;
import read_settings, distutils.util;


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
        time.sleep(2);
        curses.endwin();
        return error_msg;
   
   
    ###api initialization###
    loading_scr(main_scr,"Loading API's...");
    try:
        yt_api = yt_api_init.Init(); #still used for like/dislike
        import yt_api_request;
    except:
        return except_func("youtube api error: unable to load api");
    
    
    
    ###api information download###
    loading_scr(main_scr,"Loading YouTube Channel Info...");
    try:
        my_channel_info= yt_api_request.user_channel_info();
    except:
        return except_func("youtube api error: could not retrieve user channel info");
    
    loading_scr(main_scr,"Loading YouTube Subscription Info...");
    try:
        yt_subs = yt_api_request.user_subs();
    except:
        return except_func("youtube api error: could not retrieve subscription information");
    num_subs = len(yt_subs);
    
    
    
    ###misc initialization###
    loop = True;
    chnl_uplds = [];
    ratings = {"108":"like", "100":"dislike", "110":"none"}; # maps user input to video rating action
    
    ###read from settings file###
    try:
        max_vids = int( read_settings.get_setting("max_videos", [str(i) for i in list(range(50,1050,50))] ) );
        settings_bool = ["True","False"];
        show_e = bool( distutils.util.strtobool( read_settings.get_setting("show_emoji", settings_bool) ));
        if(not show_e): #TODO: stop removing Japanese characters
            e_filter = re.compile(r"[\U0001F1E0-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+");
        else:
            e_filter = re.compile(r"q^"); #this regex matches nothing and is efficient unless string ends in lots of "q"
        is_android = bool( distutils.util.strtobool( read_settings.get_setting("is_android", settings_bool) ));
    except:
        return except_func("could not read settings.ini. make sure variable names and values are correct");
    
    
    
    ###initialization of screens
    home_scr = curses.newwin(term_h,term_w,0,0);
    yt_scr = curses.newwin(term_h,term_w,0,0);
    sub_pad = curses.newpad(num_subs+2,term_w);
    chnl_pad = curses.newpad(max_vids+2,term_w);
    vid_scr = curses.newwin(term_h,term_w,0,0);
    
    #format: if len = 1 then [win]. if len > 1 then [pad, start_y, start_x, max_length, select_pos, list_var]
    fake_panel = [[home_scr], [yt_scr], [sub_pad,0,0,num_subs,0,yt_subs], [chnl_pad,0,0,max_vids,0,chnl_uplds], [vid_scr]];
    is_visible = [True]+[False]*4;
    in_focus = fake_panel[0];
    
    
    
    ###screen set up###
    home_scr.addstr(0,0,("Welcome to the YouTube nCurses Browser\n"
                    "Made by: Yobleck\n\n"
                    "Controls:\n"
                    "\'i\' = Goto Your Channel info\n"
                    "\'s\' = Goto Your Subscriptions\n"
                    "\'Enter\' = Select Channel from Subs or Video from Channel\n"
                    "\'Backspace\' = Go back a page\n"
                    "\'Space Bar\' = play video with mpv + youtube-dl streaming\n"
                    "\'l,d,n\' = Like/Dislike/None\n"
                    "note: you can go back to subs anytime\nbut to go back to a channel/video you must go the same way as the first time"));
    home_scr.refresh();
    
    #yt landing page with user channel info
    yt_scr.addnstr(0,0, "Channel Info:", term_w, curses.A_UNDERLINE);
    yt_scr.addstr(1,0, my_channel_info["items"][0]["snippet"]["title"], curses.A_UNDERLINE);
    yt_scr.addnstr(2,0, "Channel ID: " + my_channel_info["items"][0]["id"], term_w);
    yt_scr.addnstr(3,0, "Channel Birthday: " + my_channel_info["items"][0]["snippet"]["publishedAt"], term_w);
    
    #scrollable and clickable list of user subscriptions
    sub_pad.addstr(0,0, "My YT Subscriptions", curses.A_ITALIC | curses.A_UNDERLINE | curses.A_BOLD); #TODO: add notification of new videos on this page?
    for num, sub in enumerate(yt_subs):
        sub_pad.addnstr(num+1,0, sub["title"], term_w);
    
    
    
    while(loop):
        
        usr_input = main_scr.getch(); #TODO: pass input to screen based on is_visible
        if(usr_input == 27):
            loop = False;
        
        
        if(usr_input == 105): #i show user channel info on screen
            is_visible[0] = False;
            is_visible[1] = True; in_focus = fake_panel[1];
        
        if(usr_input == 115): #s show user subscriptions page
            is_visible[2] = True; in_focus = fake_panel[2];
            is_visible[0] = False; is_visible[1] = False; is_visible[3] = False; is_visible[4] = False;
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
                except:
                    fake_panel[3][0].erase(); fake_panel[3][0].refresh(0,0,0,0,term_h-1,term_w);
                    return except_func("youtube api error: unable to get channel uploads");
                
                #prepare channel screen for drawing videos by resetting variables
                fake_panel[3][0].erase();
                fake_panel[3][1], fake_panel[3][2], fake_panel[3][4] = [0]*3;
                fake_panel[3][0].addnstr(0,0, "Channel: " + yt_subs[in_focus[4]]["title"], term_w, curses.A_ITALIC | curses.A_UNDERLINE | curses.A_BOLD);
                fake_panel[3][5] = [];
                
                #add list of videos to screen list
                fake_panel[3][5] = list(video_list);
                fake_panel[3][3] = len(fake_panel[3][5]); #max length for scrolling
                
                #draw videos on channel screen
                for num, vid in enumerate(fake_panel[3][5]):
                    fake_panel[3][0].addnstr(num+1,0, re.sub(e_filter, " ", vid["title"]), term_w);
                is_visible[3] = True; in_focus = fake_panel[3]; is_visible[2] = False;
            
            
            elif(in_focus == fake_panel[3]):
                fake_panel[4][0].erase();
                fake_panel[4][0].addnstr(0,0,"Video: " + in_focus[5][in_focus[4]]["title"], term_w, curses.A_ITALIC | curses.A_UNDERLINE | curses.A_BOLD);
                try:
                    fake_panel[4][0].addnstr(2,0,"Thumbnail: " + in_focus[5][in_focus[4]]["thumbnails"]["maxres"]["url"], term_w);
                except:
                    fake_panel[4][0].addnstr(2,0,"Thumbnail: " + in_focus[5][in_focus[4]]["thumbnails"]["default"]["url"], term_w);
                
                #draw video url
                fake_panel[4][0].addnstr(3,0,"url: https://www.youtube.com/watch?v=" + in_focus[5][in_focus[4]]["resourceId"]["videoId"], term_w);
                fake_panel[4][0].addnstr(5,0,"Desc: " + in_focus[5][in_focus[4]]["description"].replace("\n"," "), term_w*(term_h-8));
                
                #draw like/dislike
                fake_panel[4][0].addnstr(fake_panel[4][0].getmaxyx()[0]-1,0, "Like/Dislike status: " + yt_api.videos().getRating(id=in_focus[5][in_focus[4]]["resourceId"]["videoId"]).execute()["items"][0]["rating"], term_w);
                is_visible[4] = True; in_focus = fake_panel[4]; is_visible[3] = False;
        
        
        
        if(usr_input == 32 and in_focus == fake_panel[4]): #space bar to play video
            if(is_android):
                subprocess.run(["youtube-dl","https://www.youtube.com/watch?v="+fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"]], stdout=subprocess.DEVNULL);
                subprocess.run(["termux-share","$(youtube-dl","--get-filename","https://www.youtube.com/watch?v="+fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"]+")"], stdout=subprocess.DEVNULL);
            else: #linux and hopefully windows as well
                subprocess.run([ "mpv","https://www.youtube.com/watch?v="+fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"] ], stdout=subprocess.DEVNULL);
        
        
        
        if(usr_input in [108,100,110]): #like/dislike/none with l,d,n
            yt_api.videos().rate(id=fake_panel[3][5][fake_panel[3][4]]["resourceId"]["videoId"], rating=ratings[str(usr_input)]).execute();
            fake_panel[4][0].addnstr(fake_panel[4][0].getmaxyx()[0]-1,0,"Like/Dislike status: " + ratings[str(usr_input)] + "   ", term_w);
        
        
        
        if(usr_input == 127): #backspace to go back a page
            if(in_focus == fake_panel[4]): #video to channel
                is_visible[3] = True; in_focus = fake_panel[3]; is_visible[4] = False;
            elif(in_focus == fake_panel[3]): #channels to subs
                is_visible[2] = True; in_focus = fake_panel[2]; is_visible[3] = False;
            elif(in_focus in [fake_panel[1], fake_panel[2]]): #subs and info to home
                is_visible[0] = True; in_focus = fake_panel[0]; is_visible[1] = False; is_visible[2] = False;
        
        
        
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
