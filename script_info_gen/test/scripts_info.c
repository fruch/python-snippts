
typedef struct _TEST_SCRIPT {
  unsigned int  id;
  char *        name;
  char *        subject;
  unsigned int  estimatedRunTime; //!< in sec
  void * function;
} TEST_SCRIPT;

#define TOTAL_SCRIPTS_NUM 12

TEST_SCRIPT[] tests = 
{
{1, "01. Basic - One Spot-Avail (L-P-L)", "Scripts_live_sub.c", 0 , Script_Live_Sub_01 ( void ) },
{2, "02. Basic - One Spot-Avail (L-P-L) with BG recording", "Scripts_live_sub.c", 0 , Script_Live_Sub_02 ( void ) },
{3, "03. Basic - One Spot-Avail (L-A-L) with Recording on the same live", "Scripts_live_sub.c", 0 , Script_Live_Sub_03 ( void ) },
{4, "04. Basic - Two Avails (L-A-L-A-L)", "Scripts_live_sub.c", 0 , Script_Live_Sub_04 ( void ) },
{5, "06. Basic - Two Avails (L-A-L-A-L) with BG recording", "Scripts_live_sub.c", 0 , Script_Live_Sub_06 ( void ) },
{6, "02. ON - Sending splice packet every few minutes - the same live", "Scripts_live_sub.c", 0 , Script_Stress_02 ( void ) },
{7, "01.a. Basic - One Avail - order of signaling types - case 2", "Scripts_playlist_gen.c", 0 , Script_Playlist_Gen_02 ( void ) },
{8, "01.a. Basic - One Avail - order of signaling types - case 3", "Scripts_playlist_gen.c", 0 , Script_Playlist_Gen_03 ( void ) },
{9, "01.a. Basic - One Avail - order of signaling types - case 4", "Scripts_playlist_gen.c", 0 , Script_Playlist_Gen_04 ( void ) },
{10, "01.a. Basic - One Avail - order of signaling types - case 5", "Scripts_playlist_gen.c", 0 , Script_Playlist_Gen_05 ( void ) },
{11, "01.a. Basic - One Avail - order of signaling types - case 6", "Scripts_playlist_gen.c", 0 , Script_Playlist_Gen_06 ( void ) },
{12, "01.a. Basic - One Avail - order of signaling types - case 7", "Scripts_playlist_gen.c", 0 , Script_Playlist_Gen_07 ( void ) },
};
