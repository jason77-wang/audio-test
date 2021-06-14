#!/usr/bin/env python3

import os
import sys
import struct

#define ACPI_NAMESEG_SIZE               4	/* Fixed by ACPI spec */
#define ACPI_OEM_ID_SIZE                6
#define ACPI_OEM_TABLE_ID_SIZE          8

#struct acpi_table_header {
#	char signature[ACPI_NAMESEG_SIZE];	/* ASCII table signature */
#	u32 length;		/* Length of table in bytes, including this header */
#	u8 revision;		/* ACPI Specification minor version number */
#	u8 checksum;		/* To make sum of entire table == 0 */
#	char oem_id[ACPI_OEM_ID_SIZE];	/* ASCII OEM identification */
#	char oem_table_id[ACPI_OEM_TABLE_ID_SIZE];	/* ASCII OEM table identification */
#	u32 oem_revision;	/* OEM revision number */
#	char asl_compiler_id[ACPI_NAMESEG_SIZE];	/* ASCII ASL compiler vendor ID */
#	u32 asl_compiler_revision;	/* ASL compiler version */
#}; sizeof = 0x24

#struct nhlt_acpi_table {
#	struct acpi_table_header header;
#	u8 endpoint_count;
#	struct nhlt_endpoint desc[];
#} __packed;

#struct nhlt_endpoint {
#	u32  length;
#	u8   linktype;
#	u8   instance_id;
#	u16  vendor_id;
#	u16  device_id;
#	u16  revision_id;
#	u32  subsystem_id;
#	u8   device_type;
#	u8   direction;
#	u8   virtual_bus_id;
#	struct nhlt_specific_cfg config;
#} __packed;

#struct nhlt_specific_cfg {
#	u32 size;
#	u8 caps[];
#} __packed;

#struct nhlt_device_specific_config {
#	u8 virtual_slot;
#	u8 config_type;
#} __packed;

#struct nhlt_dmic_array_config {
#	struct nhlt_device_specific_config device_config;
#	u8 array_type;
#} __packed;

#struct nhlt_vendor_dmic_array_config {
#	struct nhlt_dmic_array_config dmic_config;
#	u8 nb_mics;
#	/* TODO add vendor mic config */
#} __packed;

#enum {
#	NHLT_MIC_ARRAY_2CH_SMALL = 0xa,
#	NHLT_MIC_ARRAY_2CH_BIG = 0xb,
#	NHLT_MIC_ARRAY_4CH_1ST_GEOM = 0xc,
#	NHLT_MIC_ARRAY_4CH_L_SHAPED = 0xd,
#	NHLT_MIC_ARRAY_4CH_2ND_GEOM = 0xe,
#	NHLT_MIC_ARRAY_VENDOR_DEFINED = 0xf,
#};

#NHLT_LINK_DMIC = 2,

NHLT_LINK_DMIC = 2
NHLT_MIC_ARRAY_2CH_SMALL = 0xa
NHLT_MIC_ARRAY_2CH_BIG = 0xb
NHLT_MIC_ARRAY_4CH_1ST_GEOM = 0xc
NHLT_MIC_ARRAY_4CH_L_SHAPED = 0xd
NHLT_MIC_ARRAY_4CH_2ND_GEOM = 0xe
NHLT_MIC_ARRAY_VENDOR_DEFINED = 0xf
NHLT_FILE = "/sys/firmware/acpi/tables/NHLT"


class NhltTable:

    def __init__(self):
        self.reset()

    def reset(self):
        self.DmicNumbers = 0

    def load(self):
        try:
            f = open(NHLT_FILE, 'rb')
            """ Jump over the length of struct acpi_table_header """
            f.seek(0x24,0)
            ep_count = struct.unpack('<B', f.read(1))
            for i in range(0, ep_count[0]):
                ep_lent = struct.unpack('<L', f.read(4))
                ln_type = struct.unpack('<B', f.read(1))
                if ln_type[0] == NHLT_LINK_DMIC:
                    """ Jump over the length of struct nhlt_endpoint """
                    f.seek(20, 1)
                    array_type = struct.unpack('<B', f.read(1))
                    if (array_type[0] == NHLT_MIC_ARRAY_2CH_SMALL or
                        array_type[0] == NHLT_MIC_ARRAY_2CH_BIG):
                        self.DmicNumbers = 2
                        break
                    elif (array_type[0] == NHLT_MIC_ARRAY_4CH_1ST_GEOM or
                          array_type[0] == NHLT_MIC_ARRAY_4CH_L_SHAPED or
                          array_type[0] == NHLT_MIC_ARRAY_4CH_2ND_GEOM):
                        self.DmicNumbers = 4
                        break
                    elif (array_type[0] == NHLT_MIC_ARRAY_VENDOR_DEFINED):
                        self.DmicNumbers = struct.unpack('<B', f.read(1))[0]
                        break
                    else:
                        print ("Undefined DMIC array_type", hex(array_type[0]))
                else:
                    """ Jump to next endpoint """
                    f.seek(ep_lent[0] - 5, 1)
                    continue
        except PermissionError:
            print ('permission error, Please run it with sudo')
            self.DmicNumbers = 0
        except FileNotFoundError:
            print ('ACPI NHLT table doesn\'t exist')
            self.DmicNumbers = 0
        
