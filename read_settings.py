#provides functions for extracting values from settings.ini
import sys, re;
cwd = sys.path[0] + "/";

def get_setting(input_str, value_list): #TODO: have if statements change j in list values. with input being mode, autoplay etc.
    try: #see gtav_radio for more info
        #setting = [j for j in value_list if j in re.search(input_str + "(.+?)\\n",[i for i in open(cwd + "settings.ini","r").readlines() if input_str in i][0]).group(1)][0];
        setting = [j for j in value_list if j in [i for i in open(cwd + "settings.ini","r").readlines() if input_str in i][0]][0];
    except: #TODO: only works with true false values for now
        raise Exception("Invalid setting in settings.ini");
    return setting;

def set_setting(input_setting, input_str):
    fr = open(cwd + "settings.ini", "r").readlines() #get current settings
    for x in range(0,len(fr)):
        if(input_setting in fr[x]):
            fr[x] = input_setting + input_str + "\n";
            fw = open(cwd + "settings.ini", "w"); #overwrite new settings
            fw.writelines(fr);
            fw.close();

