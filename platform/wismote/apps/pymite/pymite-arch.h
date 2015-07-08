#include <pm.h>

PmReturn_t pymite_arch_init(void);
PmReturn_t pymite_arch_get_byte(uint8_t *b);
PmReturn_t pymite_arch_put_byte(uint8_t u8_b);
uint8_t pymite_arch_mem_get_byte(PmMemSpace_t memspace, uint8_t const **paddr);
PmReturn_t pymite_arch_get_ms_ticks(uint32_t *r_ticks);

