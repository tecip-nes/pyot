/**
 * @author Daniele Alessandrelli
 *
 */

/* we must reundef list-related function names to avoid collision 
 * with list-functions undefd in Contiki
 */
#undef list_new
#undef list_getItem
#undef list_setItem
#undef list_copy
#undef list_append
#undef list_replicate
#undef list_insert
#undef list_remove
#undef list_index
#undef list_delItem
#undef list_print
#undef list_clear
