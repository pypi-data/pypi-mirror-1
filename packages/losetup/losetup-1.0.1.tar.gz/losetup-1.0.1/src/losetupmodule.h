#ifndef _LOSETUP_MODULE_H
#define _LOSETUP_MODULE_H


#define LOOP_SET_FD		0x4C00
#define LOOP_CLR_FD		0x4C01
#define LOOP_SET_STATUS		0x4C02
#define LOOP_GET_STATUS		0x4C03
#define LOOP_SET_STATUS64	0x4C04
#define LOOP_GET_STATUS64	0x4C05

/* Flags for loop_into{64,}->lo_flags */
enum {
	LO_FLAGS_READ_ONLY  = 1,
	LO_FLAGS_USE_AOPS   = 2,
	LO_FLAGS_AUTOCLEAR  = 4, /* New in 2.6.25 */
};

#define LO_NAME_SIZE	64
#define LO_KEY_SIZE	32

struct loop_info64 {
	uint64_t	lo_device;
	uint64_t	lo_inode;
	uint64_t	lo_rdevice;
	uint64_t	lo_offset;
	uint64_t	lo_sizelimit; /* bytes, 0 == max available */
	uint32_t	lo_number;
	uint32_t	lo_encrypt_type;
	uint32_t	lo_encrypt_key_size;
	uint32_t	lo_flags;
	uint8_t		lo_file_name[LO_NAME_SIZE];
	uint8_t		lo_crypt_name[LO_NAME_SIZE];
	uint8_t		lo_encrypt_key[LO_KEY_SIZE];
	uint64_t	lo_init[2];
};

#endif//_LOSETUP_MODULE_H
