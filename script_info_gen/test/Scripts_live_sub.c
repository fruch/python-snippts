#include "xAd.h"

/** @brief	Name:	01. Basic - One Spot-Avail (L-P-L) 
 *					01. Basic - Sending splice info packet with an existing Ad and a valid Rule
 *			Notes: */ 
XSTATUS Script_Live_Sub_01 ( void ) {
	
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
    
    SCRIPT_NAME("01. Basic - One Spot-Avail (L-P-L)");
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	//TODO JU@NDS we need to add exot points in case of failed of this function 

	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();

		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 700 /*Frames before Avail*/, XTRUE);		

		DELAY (1000 /* 1 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (4000 /* 4 sec */);

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	status = xAd_TermScript (script_name);
	
	return XSTATUS_OK;
}

/** @brief	Name: 02. Basic - One Spot-Avail (L-P-L) with BG recording 
 *			Notes: */
XSTATUS Script_Live_Sub_02 ( void ) {

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
    
    SCRIPT_NAME("02. Basic - One Spot-Avail (L-P-L) with BG recording");

	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);

	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();

		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
	
		xAd_Wrapper_StartCurrentRecording("Live-2", 3 /* mins */);
		
		DELAY (24000 /* 24 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (3000  /* 3 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);

		xAd_Wrapper_StopCurrentRecording("Live-2");
	}

	status = xAd_TermScript (script_name);

	return status;
}


/** @brief	Name: 03. Basic - One Spot-Avail (L-A-L) with Recording on the same live
 *			Notes: */ 
XSTATUS Script_Live_Sub_03 ( void ) {

	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("03. Basic - One Spot-Avail (L-A-L) with Recording on the same live");

	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);

	/* Test Start */
	{
		status = xAd_TEST_START_Sequence ();

		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
	
		xAd_Wrapper_StartCurrentRecording("Live-1", 3 /* mins */);

		DELAY (22000 /* 22 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (3000  /* 3 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);


		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);

		xAd_Wrapper_StopCurrentRecording("Live-1");
	}

	status = xAd_TermScript (script_name);

	return status;
}


/** @brief	Name: 04. Basic - Two Avails (L-A-L-A-L)
 *			Notes: */ 
XSTATUS Script_Live_Sub_04 ( void ) {

	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("04. Basic - Two Avails (L-A-L-A-L)");
	
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	
	/* Test Start */
	{
		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
	
		status = xAd_TEST_START_Sequence ();

		DELAY (26000 /* 26 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (3000  /* 3 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);


		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	/* Sec. Splice Info */
	{
		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
		status = xAd_AppendPlayList(playlist_string, 0);

		status = xAd_TEST_START_Sequence ();

		DELAY (26000 /* 26 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (3000  /* 3 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);


		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}

	status = xAd_TermScript (script_name);

	return status;
}

/** @brief	Name: 06. Basic - Two Avails (L-A-L-A-L) with BG recording
 *			Notes: */ 
XSTATUS Script_Live_Sub_06 ( void ) {

	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("06. Basic - Two Avails (L-A-L-A-L) with BG recording");
	
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	
	/* Test Start */
	{

		status = xAd_TEST_START_Sequence ();

		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
	
		xAd_Wrapper_StartCurrentRecording("Live-2", 20 /* mins */);

		DELAY (25000 /* 25 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (4000  /* 4 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);


		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	/* Sec. Splice Info */
	{
		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
		status = xAd_AppendPlayList(playlist_string, 0);

		status = xAd_TEST_START_Sequence ();

		DELAY (25000 /* 25 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (4000  /* 4 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}

	status = xAd_TermScript (script_name);

	return status;
}

/** @brief	Name: 02. ON - Sending splice packet every few minutes - the same live 
 *			Notes: Currently the loop is 5 time (can be change loopSize to bigger value) */ 
XSTATUS Script_Stress_02 ( void ) {

	HUNTER_EXPECTED expected;
	XBOOL  isBlocking = XTRUE;
	XSTATUS status = XSTATUS_OK;
	
	int runTimeInSec = 70;
	XBOOL isSeqOK = XTRUE;
	int loopSize = 5; /* How many Avails will be during this stress */
	int i = 0;

	/* Test Init */
	char *playlist_string  = "LIVE , Live-1 , in:Avail-1\n \
						      RECORD , Ad-1 , in:BOF out:EOF\n \
						      LIVE , Live-1 , out:Avail-1\n"; 
    
    SCRIPT_NAME("02. ON - Sending splice packet every few minutes - the same live");
	
	status = xAd_InitScript (script_name);

	status = xAd_BuildPlayList(playlist_string, 0);
	
	/* Test Start */
	{

		status = xAd_TEST_START_Sequence ();

		status = xAd_Wrapper_StartLive("Live-1");

		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
	
		DELAY (30000 /* 30 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (400  /* 0.4 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}
	/* Sec. Splice Info */
	for (i=0; i< loopSize ; i++)
	{
		XAPP_Debug(XSTATUS_OK,"Script Loop = [%d]", i);

		status = xAd_ScriptSync(0, "Avail-1", 1000 /*Frames before Avail*/, XTRUE);
		status = xAd_AppendPlayList(playlist_string, 0);

		status = xAd_TEST_START_Sequence ();

		DELAY (30000 /* 30 sec */);

		status = xAd_PrepareSignaling(RULES0); /* Rules for Avail-1 */
		status = xAd_SignalRules_ToLive(RULES0, XTRUE);
		
		DELAY (400  /* 0.4 sec */ );

		status = xAd_PrepareSignaling(SPLICE0); /* Splice for Avail-1 */
		status = xAd_SignalSplice_ToLive(SPLICE0, XTRUE);

		status = xAd_Hunter_Run(runTimeInSec, isBlocking, &expected);
		status = xAd_PrintHunterResults();
	
		status = xAd_TEST_END_Sequence (0, &isSeqOK);
	}

	status = xAd_TermScript (script_name);

	return status;
}
