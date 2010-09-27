
/** @brief	Name:	01. Basic - One Spot-Avail (L-P-L) 
 *					01. Basic - Sending splice info packet with an existing Ad and a valid Rule
 *			Notes: */
extern XSTATUS Script_Live_Sub_01 ( void );
/** @brief	Name: 02. Basic - One Spot-Avail (L-P-L) with BG recording 
 *			Notes: */
extern XSTATUS Script_Live_Sub_02 ( void );
/** @brief	Name: 03. Basic - One Spot-Avail (L-A-L) with Recording on the same live
 *			Notes: */
extern XSTATUS Script_Live_Sub_03 ( void );
/** @brief	Name: 04. Basic - Two Avails (L-A-L-A-L)
 *			Notes: */
extern XSTATUS Script_Live_Sub_04 ( void );
/** @brief	Name: 06. Basic - Two Avails (L-A-L-A-L) with BG recording
 *			Notes: */
extern XSTATUS Script_Live_Sub_06 ( void );
/** @brief	Name: 02. ON - Sending splice packet every few minutes - the same live 
 *			Notes: Currently the loop is 5 time (can be change loopSize to bigger value) */
extern XSTATUS Script_Stress_02 ( void );
/** @brief	Name: 01.a. Basic - One Avail - order of signaling types - case 2
 *			Desc:	----R-----|-- Avail-1 --|---- 
 *			Expected: Sub. won't happen
 */
extern XSTATUS Script_Playlist_Gen_02 ( void );
/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 3
 *			Desc:	--R1--R2--S----|-- Avail-1 --|----
 *			Expected: Sub. happens ( R1 discarded, R2 is used for Sub.)
 */
extern XSTATUS Script_Playlist_Gen_03 ( void );
/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 4
 *			Desc:	S1 and S2 - out packet
 *					--R---S1--S2---|-- Avail-1 --|--------
 *			Expected: Sub. happend ( S2 discarded  )
 */
extern XSTATUS Script_Playlist_Gen_04 ( void );
/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 5
 *			Desc:	S1 out, S2 in
 *					--R---S1--S2---|-- Avail-1 --|--------
 *			Expected: Sub. happend ( in M1, S2 discarded)
 */
extern XSTATUS Script_Playlist_Gen_05 ( void );
/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 6
 *			Desc:	
 *					---------S--------|-- Avail-1 --|--------
 *			Expected: Sub. won't happen (S discarded)
 */
extern XSTATUS Script_Playlist_Gen_06 ( void );
/** @brief	Name:  01.a. Basic - One Avail - order of signaling types - case 7
 *			Desc:	
 *					-----R1--S--R2--|-- Avail-1 --|--------
 *			Expected: Sub. happens (R1 is used)
 */
extern XSTATUS Script_Playlist_Gen_07 ( void );
