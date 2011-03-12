#include "xAd.h"
/** @brief	Name: 01.a. Basic - One Avail - order of signaling types - case 2
 *			Desc:	----R-----|-- Avail-1 --|---- 
 *			Expected: Sub. won't happen
 */
XSTATUS Script_Playlist_Gen_02 ( void )
{
	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	XCONNECTION xcon = XCONNECTION_INVALID;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 \n"; 
    
    SCRIPT_NAME("01.a. Basic - One Avail - order of signaling types - case 2");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();

		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 700 /*Frames before Avail*/, XTRUE);

		DELAY (4000 /* 4 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		/* NO splice is being sent */ 

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}


/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 3
 *			Desc:	--R1--R2--S----|-- Avail-1 --|----
 *			Expected: Sub. happens ( R1 discarded, R2 is used for Sub.)
 */
XSTATUS Script_Playlist_Gen_03 ( void )
{
		
	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	XCONNECTION xcon = XCONNECTION_INVALID;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("01.a. Basic - One Avail - order of signaling types - case 3");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();
		status = xAd_Wrapper_StartLive("Live-1");
		status = xAd_ScriptSync(0, "Avail-1", 600 /*Frames before Avail*/, XTRUE);
	
	
		DELAY (1000);

		status = xAd_PrepareSignaling(RULES1); /* Bad Rules, one that can't be used */
		status = xAd_SignalRules_ToLive(RULES1, XTRUE);

		DELAY (1000);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (1000);

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}

/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 4
 *			Desc:	S1 and S2 - out packet
 *					--R---S1--S2---|-- Avail-1 --|--------
 *			Expected: Sub. happend ( S2 discarded  )
 */
XSTATUS Script_Playlist_Gen_04 ( void )
{
		
	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	XCONNECTION xcon = XCONNECTION_INVALID;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("01.a. Basic - One Avail - order of signaling types - case 4");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);

	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();
		status = xAd_Wrapper_StartLive("Live-1");
		status = xAd_ScriptSync(0, "Avail-1", 600 /*Frames before Avail*/, XTRUE);
	
		DELAY (200);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (200);

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);
		
		DELAY (200);

		status = xAd_PrepareSignaling(SPLICE1); /* Bad Splice one that can't be used (splice_null) */
		status = xAd_SignalSplice_ToLive(SPLICE1, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}

/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 5
 *			Desc:	S1 out, S2 in
 *					--R---S1--S2---|-- Avail-1 --|--------
 *			Expected: Sub. happend ( in M1, S2 discarded)
 */
XSTATUS Script_Playlist_Gen_05 ( void )
{
		
	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	XCONNECTION xcon = XCONNECTION_INVALID;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("01.a. Basic - One Avail - order of signaling types - case 5");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();
		status = xAd_Wrapper_StartLive("Live-1");
		status = xAd_ScriptSync(0, "Avail-1", 600 /*Frames before Avail*/, XTRUE);

		DELAY (200);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (200);

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);
		
		DELAY (200);

		status = xAd_PrepareSignaling(SPLICE2); /* In Splice event */
		status = xAd_SignalSplice_ToLive(SPLICE2, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}

/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 6
 *			Desc:	
 *					---------S--------|-- Avail-1 --|--------
 *			Expected: Sub. won't happen (S discarded)
 */
XSTATUS Script_Playlist_Gen_06 ( void )
{
		
	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	XCONNECTION xcon = XCONNECTION_INVALID;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1\n"; 
    
    SCRIPT_NAME("01.a. Basic - One Avail - order of signaling types - case 6");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();
		status = xAd_Wrapper_StartLive("Live-1");
		status = xAd_ScriptSync(0, "Avail-1", 600 /*Frames before Avail*/, XTRUE);
		
		DELAY (400);
		RULES_N_SPLICE_SHOULD_FAIL;

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);
		

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}
/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 7
 *			Desc:	
 *					-----R1--S--R2--|-- Avail-1 --|--------
 *			Expected: Sub. happens (R1 is used)
 */
XSTATUS Script_Playlist_Gen_07 ( void )
{
		
	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	XCONNECTION xcon = XCONNECTION_INVALID;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("01.a. Basic - One Avail - order of signaling types - case 7");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);

	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();
		status = xAd_Wrapper_StartLive("Live-1");
		status = xAd_ScriptSync(0, "Avail-1", 600 /*Frames before Avail*/, XTRUE);	

		DELAY (200);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (200);

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);
		
		DELAY (200);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}

