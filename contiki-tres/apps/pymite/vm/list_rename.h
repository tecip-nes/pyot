/**
 * @author Daniele Alessandrelli
 *
 */

/* we must redefine list-related function names to avoid collision 
 * with list-functions defined in Contiki
 */
#define list_new        pm_list_new        
#define list_getItem    pm_list_getItem
#define list_setItem    pm_list_setItem
#define list_copy       pm_list_copy
#define list_append     pm_list_append
#define list_replicate  pm_list_replicate
#define list_insert     pm_list_insert
#define list_remove     pm_list_remove
#define list_index      pm_list_index
#define list_delItem    pm_list_delItem
#define list_print      pm_list_print
#define list_clear      pm_list_clear
